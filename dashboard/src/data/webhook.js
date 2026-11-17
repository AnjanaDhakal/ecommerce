import { createResource } from 'frappe-ui'

const webhook = createResource({
    url: '/api/method/ecommerce.webhook.get_webhook_url_status',
    auto: true, // required, since it should start fetching automatically
    cache: 'webhook',
    method: 'GET'
})

export default webhook
