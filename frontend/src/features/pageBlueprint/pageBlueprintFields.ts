export interface PageBlueprintSection {
  id?: number
  type: string
  name: string
  purpose: string
  position: number
  is_optional: boolean
}

export interface PageBlueprintFields {
  name: string
  description: string
  sections: PageBlueprintSection[]
}
