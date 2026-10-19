import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from api.routes.chat_routes import router
from application.handlers.chat import chat_handlers
from domain.models import models
from domain.models.chat.chat_conversation import ChatConversation
from domain.models.chat.chat_message import ChatMessage
from infrastructure.database.db import Base
from infrastructure.repositories.chat_repository import ChatRepository


class ChatTests(unittest.TestCase):
    CONTEXT = {"type": "offer_profile", "id": 1, "include": ["offer_source", "marketing_angle"], "marketing_angle_ids": [3]}

    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})

        @event.listens_for(self.engine, "connect")
        def enable_fk(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.repo = ChatRepository(None, self.db)
        self.compose_calls = []
        self.sent = []
        self.answer = "Odpowiedź asystenta"
        self.num_ctx = 65536

        def compose(**options):
            self.compose_calls.append(options)
            if options["root"].id == 999:
                raise LookupError("Offer profile not found")
            return "<offer_profile>Keliro PerfectFit</offer_profile>"

        def chat_llm(messages, **kwargs):
            self.sent.append((messages, kwargs))
            return SimpleNamespace(content=self.answer, prompt_tokens=1234, completion_tokens=56)

        container = SimpleNamespace(
            chat_repository=lambda: self.repo,
            llm_context_composer=lambda: SimpleNamespace(compose=compose),
            ai_service=lambda: SimpleNamespace(chat_llm=chat_llm, ollama_service=SimpleNamespace(num_ctx=self.num_ctx)),
        )
        self.patcher = patch.object(chat_handlers, "Container", lambda: container)
        self.patcher.start()
        app = FastAPI(); app.include_router(router); self.client = TestClient(app)

    def tearDown(self):
        self.client.close(); self.patcher.stop(); self.db.close(); self.engine.dispose()

    def create(self, **payload):
        response = self.client.post("/chat/conversations", json={"context": self.CONTEXT, **payload})
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_conversation_is_saved_with_messages_and_context(self):
        conversation = self.create()
        self.assertEqual(conversation["title"], "")
        self.assertEqual(conversation["context"]["marketing_angle_ids"], [3])
        response = self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": "  Jakie są zalety produktu?  "})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual([m["role"] for m in response.json()["messages"]], ["user", "assistant"])
        self.assertEqual(response.json()["conversation"]["title"], "Jakie są zalety produktu?")
        loaded = self.client.get(f"/chat/conversations/{conversation['id']}").json()
        self.assertEqual([m["content"] for m in loaded["messages"]], ["Jakie są zalety produktu?", "Odpowiedź asystenta"])
        self.assertEqual([item["id"] for item in self.client.get("/chat/conversations").json()], [conversation["id"]])

    def test_new_resource_selections_are_saved_and_used_in_chat(self):
        context = {"type": "offer_profile", "id": 1,
                   "include": ["analysis", "checklist", "page_blueprint", "page", "note"],
                   "analysis_ids": [11], "checklist_ids": [12], "page_blueprint_ids": [13],
                   "page_ids": [14], "note_ids": [15]}
        response = self.client.post("/chat/conversations", json={"context": context})
        self.assertEqual(response.status_code, 201, response.text)
        conversation = response.json()
        self.assertEqual(conversation["context"]["page_blueprint_ids"], [13])
        self.assertEqual(conversation["context"]["note_ids"], [15])
        self.assertEqual([selection.include_ids for selection in self.compose_calls[-1]["include"]],
                         [(11,), (12,), (13,), (14,), (15,)])
        loaded = self.client.get(f"/chat/conversations/{conversation['id']}").json()
        self.assertEqual(loaded["context"]["page_ids"], [14])
        preview = self.client.get(f"/chat/conversations/{conversation['id']}/context")
        self.assertEqual(preview.status_code, 200, preview.text)
        self.assertTrue(preview.headers["content-type"].startswith("text/plain"))
        self.assertEqual(self.compose_calls[-1]["include"][-1].include_ids, (15,))

    def test_prompt_contains_fresh_context_and_full_history(self):
        conversation = self.create(title="Moja rozmowa")
        for content in ("Pierwsze pytanie", "Drugie pytanie"):
            self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": content})
        messages, kwargs = self.sent[-1]
        self.assertEqual(messages[0].role.value, "system")
        self.assertIn("<offer_profile>Keliro PerfectFit</offer_profile>", messages[0].content)
        self.assertEqual([(m.role.value, m.content) for m in messages[1:]], [
            ("user", "Pierwsze pytanie"), ("assistant", "Odpowiedź asystenta"), ("user", "Drugie pytanie"),
        ])
        self.assertNotIn("rule_sets", kwargs)
        self.assertEqual(self.compose_calls[-1]["include"][1].include_ids, (3,))
        self.assertEqual(self.client.get(f"/chat/conversations/{conversation['id']}").json()["title"], "Moja rozmowa")

    def test_old_messages_are_trimmed_to_fit_the_model_context(self):
        conversation = self.create()
        for content in ("A" * 6000, "B" * 6000, "C" * 6000):
            self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": content})
        self.num_ctx = 4096 + 5000
        self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": "Ostatnie"})
        history = [m.content for m in self.sent[-1][0][1:]]
        self.assertEqual(history[-1], "Ostatnie")
        self.assertNotIn("A" * 6000, history)
        self.assertLess(sum(map(len, history)), 5000 * 3)

    def test_usage_reports_context_history_and_limit(self):
        conversation = self.create()
        empty = self.client.get(f"/chat/conversations/{conversation['id']}/usage").json()
        self.assertEqual((empty["history_tokens"], empty["messages_total"], empty["limit_tokens"]), (0, 0, 65536))
        self.assertGreater(empty["context_tokens"], 0)
        self.assertFalse(empty["too_large"])
        self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": "Q" * 300})
        usage = self.client.get(f"/chat/conversations/{conversation['id']}/usage").json()
        expected_history = -(-(300 + len(self.answer)) // 3)
        self.assertEqual((usage["history_tokens"], usage["messages_in_context"], usage["messages_total"]), (expected_history, 2, 2))
        self.assertEqual(usage["used_tokens"], usage["context_tokens"] + expected_history)
        self.num_ctx = 4096 + 50
        self.assertTrue(self.client.get(f"/chat/conversations/{conversation['id']}/usage").json()["too_large"])
        self.assertEqual(self.client.get("/chat/conversations/999/usage").status_code, 404)

    def conversation_with_two_turns(self):
        conversation = self.create(title="Rozmowa")
        for index, content in enumerate(("Pytanie 1", "Pytanie 2")):
            self.answer = f"Odpowiedź {index + 1}"
            self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": content})
        return conversation["id"], self.client.get(f"/chat/conversations/{conversation['id']}").json()["messages"]

    def contents(self, conversation_id):
        return [m["content"] for m in self.client.get(f"/chat/conversations/{conversation_id}").json()["messages"]]

    def test_exact_model_token_counts_are_stored_and_reported(self):
        conversation_id, messages = self.conversation_with_two_turns()
        self.assertEqual((messages[1]["prompt_tokens"], messages[1]["completion_tokens"]), (1234, 56))
        self.assertIsNone(messages[0]["prompt_tokens"])
        usage = self.client.get(f"/chat/conversations/{conversation_id}/usage").json()
        self.assertEqual((usage["last_prompt_tokens"], usage["last_completion_tokens"]), (1234, 56))

    def test_fork_copies_history_up_to_message_and_keeps_source(self):
        conversation_id, messages = self.conversation_with_two_turns()
        response = self.client.post(f"/chat/messages/{messages[1]['id']}/fork")
        self.assertEqual(response.status_code, 201, response.text)
        fork = response.json()
        self.assertNotEqual(fork["id"], conversation_id)
        self.assertEqual(fork["title"], "Rozmowa (fork)")
        self.assertEqual(fork["context"], self.CONTEXT | {key: value for key, value in fork["context"].items() if key not in self.CONTEXT})
        self.assertEqual([m["content"] for m in fork["messages"]], ["Pytanie 1", "Odpowiedź 1"])
        self.assertEqual(len(self.contents(conversation_id)), 4)

    def test_delete_single_message(self):
        conversation_id, messages = self.conversation_with_two_turns()
        response = self.client.delete(f"/chat/messages/{messages[1]['id']}/delete")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual([m["content"] for m in response.json()["messages"]], ["Pytanie 1", "Pytanie 2", "Odpowiedź 2"])
        self.assertEqual(self.client.delete("/chat/messages/999/delete").status_code, 404)

    def test_regenerate_replaces_answer_and_later_messages(self):
        conversation_id, messages = self.conversation_with_two_turns()
        self.answer = "Nowa odpowiedź"
        response = self.client.post(f"/chat/messages/{messages[1]['id']}/regenerate")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.contents(conversation_id), ["Pytanie 1", "Nowa odpowiedź"])
        self.assertEqual([m.content for m in self.sent[-1][0][1:]], ["Pytanie 1"])
        self.assertEqual(self.client.post(f"/chat/messages/{messages[0]['id']}/regenerate").status_code, 422)

    def test_edit_user_message_answers_again_from_that_point(self):
        conversation_id, messages = self.conversation_with_two_turns()
        self.answer = "Odpowiedź na zmienione"
        response = self.client.post(f"/chat/messages/{messages[0]['id']}/edit", json={"content": "Zmienione pytanie"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.contents(conversation_id), ["Zmienione pytanie", "Odpowiedź na zmienione"])
        self.assertEqual(self.client.post(f"/chat/messages/{messages[1]['id']}/edit", json={"content": "x"}).status_code, 422)

    def test_update_specific_user_and_generated_messages_in_place(self):
        conversation_id, messages = self.conversation_with_two_turns()
        original_ids = [message["id"] for message in messages]
        for message, content in ((messages[0], "Poprawione pytanie"), (messages[1], "Poprawiona odpowiedź AI")):
            response = self.client.post(f"/chat/messages/{message['id']}/update", json={"content": content})
            self.assertEqual(response.status_code, 200, response.text)
        loaded = self.client.get(f"/chat/conversations/{conversation_id}").json()["messages"]
        self.assertEqual([message["id"] for message in loaded], original_ids)
        self.assertEqual([message["content"] for message in loaded],
                         ["Poprawione pytanie", "Poprawiona odpowiedź AI", "Pytanie 2", "Odpowiedź 2"])
        self.assertIsNone(loaded[1]["prompt_tokens"])
        self.assertIsNone(loaded[1]["completion_tokens"])
        self.assertEqual(self.client.post(f"/chat/messages/{messages[1]['id']}/update", json={"content": " "}).status_code, 422)
        self.assertEqual(self.client.post("/chat/messages/999/update", json={"content": "x"}).status_code, 404)

    def test_failed_regenerate_or_edit_keeps_everything(self):
        conversation_id, messages = self.conversation_with_two_turns()
        self.answer = " "
        self.assertEqual(self.client.post(f"/chat/messages/{messages[1]['id']}/regenerate").status_code, 502)
        self.assertEqual(self.client.post(f"/chat/messages/{messages[0]['id']}/edit", json={"content": "Nowe"}).status_code, 502)
        self.assertEqual(self.contents(conversation_id), ["Pytanie 1", "Odpowiedź 1", "Pytanie 2", "Odpowiedź 2"])

    def test_update_delete_and_validation(self):
        conversation = self.create()
        updated = self.client.post(f"/chat/conversations/{conversation['id']}/update", json={"title": "Nowy tytuł", "context": {**self.CONTEXT, "include": ["offer_source"], "marketing_angle_ids": []}})
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual((updated.json()["title"], updated.json()["context"]["include"]), ("Nowy tytuł", ["offer_source"]))
        self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": "Pytanie"})
        self.assertEqual(self.client.delete(f"/chat/conversations/{conversation['id']}/delete").status_code, 200)
        self.assertEqual((self.db.query(ChatConversation).count(), self.db.query(ChatMessage).count()), (0, 0))
        self.assertEqual(self.client.post("/chat/conversations", json={"context": {**self.CONTEXT, "id": 999}}).status_code, 404)
        self.assertEqual(self.client.post("/chat/conversations", json={"context": {**self.CONTEXT, "marketing_angle_ids": []}}).status_code, 422)
        self.assertEqual(self.client.post("/chat/conversations/999/messages", json={"content": "x"}).status_code, 404)
        self.assertEqual(self.client.get("/chat/conversations/999").status_code, 404)

    def test_failed_answer_saves_nothing(self):
        conversation = self.create()
        self.answer = "   "
        self.assertEqual(self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": "Pytanie"}).status_code, 502)
        self.assertEqual(self.db.query(ChatMessage).count(), 0)
        self.assertEqual(self.client.post(f"/chat/conversations/{conversation['id']}/messages", json={"content": " "}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
