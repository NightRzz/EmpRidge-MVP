/** Zwraca identyfikator filmu dla osadzenia iframe YouTube lub null. */
export function youtubeEmbedVideoId(raw: string | null | undefined): string | null {
  if (!raw?.trim()) return null

  const url = raw.trim()

  try {
    const parsed = url.startsWith('http') ? new URL(url) : new URL(`https://${url}`)
    const host = parsed.hostname.replace(/^www\./, '')

    if (host === 'youtu.be') {
      const id = parsed.pathname.split('/').filter(Boolean)[0]
      return id && /^[\w-]{11}$/.test(id) ? id : null
    }

    if (host === 'youtube.com' || host === 'm.youtube.com' || host === 'music.youtube.com') {
      const v = parsed.searchParams.get('v')
      if (v && /^[\w-]{11}$/.test(v)) return v

      const pathParts = parsed.pathname.split('/').filter(Boolean)
      const embedIdx = pathParts.indexOf('embed')
      if (embedIdx >= 0 && pathParts[embedIdx + 1] && /^[\w-]{11}$/.test(pathParts[embedIdx + 1]!)) {
        return pathParts[embedIdx + 1]!
      }

      const shortIdx = pathParts.indexOf('shorts')
      if (shortIdx >= 0 && pathParts[shortIdx + 1] && /^[\w-]{11}$/.test(pathParts[shortIdx + 1]!)) {
        return pathParts[shortIdx + 1]!
      }
    }
  } catch {
    // ignore
  }

  const watchMatch = url.match(/[?&]v=([\w-]{11})/)
  if (watchMatch?.[1]) return watchMatch[1]

  const shortsMatch = url.match(/youtube\.com\/shorts\/([\w-]{11})/)
  if (shortsMatch?.[1]) return shortsMatch[1]

  return null
}
