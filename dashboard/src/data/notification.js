import { createResource } from 'frappe-ui'

const notification = createResource({

    url: '/api/method/ecommerce.ecommerce.doctype.ecommerce_push_notification_log.api.get_notification',

    auto: true, // required, since it should start fetching automatically
    cache: 'notification',
    method: 'GET',
})


export default notification;
