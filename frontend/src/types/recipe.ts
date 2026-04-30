export type Recipe = {
  id: number
  title: string
  instructions: string | null
  image_url: string | null
  youtube_url: string | null
  category_id: number | null
  area_id: number | null
}
