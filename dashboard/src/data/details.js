import { createResource } from 'frappe-ui'

const details = createResource({

    url: '/api/method/ecommerce.api.get_vendor_order_status_comment_details',

    auto: true, // required, since it should start fetching automatically
    cache: 'details',
    method: 'GET',
})


export default details;
