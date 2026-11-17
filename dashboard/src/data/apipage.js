import { createResource } from 'frappe-ui'

const page = createResource({

    url: '/api/method/ecommerce.api.get_vendor_messenger_page',

    auto: true, // required, since it should start fetching automatically
    cache: 'page',
    method: 'GET',
})


export default page;
