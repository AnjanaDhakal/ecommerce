import { createResource } from 'frappe-ui'

const chat = createResource({

    url: '/api/method/ecommerce.api.get_payment_chat',

    auto: true, // required, since it should start fetching automatically
    cache: 'chat',
    method: 'GET',
})


export default chat;
