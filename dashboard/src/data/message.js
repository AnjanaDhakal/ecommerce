import { createResource } from 'frappe-ui'

const message = createResource({

    url: '/api/method/ecommerce.api.get_message',

    auto: true, // required, since it should start fetching automatically
    cache: 'message',
    method: 'GET',
})


export default message;
