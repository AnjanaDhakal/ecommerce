import { createResource } from 'frappe-ui'

const vendorProfile = createResource({
    url: '/api/method/ecommerce.api.vendor_details',
    auto: true, // required, since it should start fetching automatically
    cache: 'vendor-profile'
})

export default vendorProfile
