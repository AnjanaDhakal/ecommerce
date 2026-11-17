


import { createResource } from 'frappe-ui'

const orderwisepayment = createResource({
    url: '/api/method/ecommerce.api.get_orderwise_payment',
    auto: false, // you can fetch manually
    method: 'GET',
    cache: false,
})


export default orderwisepayment;
