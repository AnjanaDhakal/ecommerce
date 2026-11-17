import { createResource } from 'frappe-ui'

const webhookcomment = createResource({
    url: '/api/method/ecommerce.webhook.get_webhook_url_comment',
    auto: true, // required, since it should start fetching automatically
    cache: 'webhookcomment',
    method: 'GET'
})

export default webhookcomment
