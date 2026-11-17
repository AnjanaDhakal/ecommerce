import { createResource } from 'frappe-ui'

const newuser = createResource({

    url: '/api/method/ecommerce.api.get_vendor_employee_info',

    auto: true, // required, since it should start fetching automatically
    cache: 'newuser',
    method: 'GET',
})


export default newuser;
