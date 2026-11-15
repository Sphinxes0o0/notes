// Exclude VitePress controls from the index while retaining prose and source code.
export async function renderSearchContent(source, env, md) {
  const html = await md.renderAsync(source, env)
  if (env.frontmatter?.search === false) return ''

  // Keep heading permalinks: VitePress uses them to split search sections.
  return html
    .replace(/<div class="line-numbers-wrapper"[^>]*>[\s\S]*?<\/div>/g, '')
    .replace(/<button\b[^>]*\bclass="copy"[^>]*>[\s\S]*?<\/button>/g, '')
    .replace(/<span class="lang">[^<]*<\/span>/g, '')
}
