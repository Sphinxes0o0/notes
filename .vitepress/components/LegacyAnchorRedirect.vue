<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import { useRouter, withBase } from 'vitepress'

const props = defineProps({ targets: { type: Object, required: true } })
const router = useRouter()

function redirect() {
  let anchor
  try {
    anchor = decodeURIComponent(window.location.hash.slice(1))
  } catch {
    return
  }
  const target = props.targets[anchor]
  if (target) router.go(withBase(target))
}

onMounted(() => {
  redirect()
  window.addEventListener('hashchange', redirect)
})
onBeforeUnmount(() => window.removeEventListener('hashchange', redirect))
</script>

<template><span hidden aria-hidden="true"></span></template>
