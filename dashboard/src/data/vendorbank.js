import { createResource } from 'frappe-ui'

const vendorbank = createResource({
    url: '/api/method/ecommerce.api.vendor_bank_details',
    auto: true, // required, since it should start fetching automatically
    cache: 'vendorbank',
    method: 'GET'
})

export default vendorbank
