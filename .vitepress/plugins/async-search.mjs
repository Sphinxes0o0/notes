// VitePress alpha.12 restores the full index synchronously. Yield between batches
// so opening search does not block input while thousands of sections are restored.
export function asyncSearchPlugin() {
  return {
    name: 'notes:async-search',
    enforce: 'pre',
    transform(code, id) {
      if (!id.split('?')[0].endsWith('/VPLocalSearchBox.vue') || id.includes('?')) return
      const call = 'MiniSearch.loadJSON<Result>('
      if (!code.includes(call)) throw new Error('VitePress search loader changed; review the async search adapter')
      return code.replace(call, 'await MiniSearch.loadJSONAsync<Result>(')
        .replace('(await searchIndexData.value[localeIndex.value]?.())?.default,', 'await (await searchIndexData.value[localeIndex.value]?.())?.default,')
    }
  }
}
