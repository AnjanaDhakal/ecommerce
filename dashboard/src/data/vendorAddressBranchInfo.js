import { createResource } from 'frappe-ui'

const vendorAddressBranchInfo = createResource({

    url: '/api/method/ecommerce.api.get_vendor_address_branch',

    auto: true, // required, since it should start fetching automatically
    cache: 'vendor-address-branch',
    method: 'GET',
})


export default vendorAddressBranchInfo;
