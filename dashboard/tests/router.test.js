import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const routerSource = readFileSync(new URL('../src/router.js', import.meta.url), 'utf8')

test('routes only the ecommerce builder and storefront', () => {
  assert.match(routerSource, /path: '\/website'/)
  assert.match(routerSource, /path: '\/store\/:websiteId'/)
  assert.doesNotMatch(routerSource, /logi360/i)
})
