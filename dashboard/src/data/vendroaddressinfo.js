import { createResource } from 'frappe-ui'

const vendroaddressinfo = createResource({

    url: '/api/method/ecommerce.api.get_vendor_address_info',

    auto: true, // required, since it should start fetching automatically
    cache: 'addressinfo',
    method: 'GET',
})


export default vendroaddressinfo;
