
import { createResource } from 'frappe-ui'

const codtransfer = createResource({

    url: '/api/method/ecommerce.api.get_cod_transfer',

    auto: true, // required, since it should start fetching automatically
    cache: 'codtransfer',
    method: 'GET',
})


export default codtransfer;
