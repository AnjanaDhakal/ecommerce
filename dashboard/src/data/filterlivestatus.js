import { createResource } from 'frappe-ui'

const filterlivestatus = createResource({

    url: '/api/method/ecommerce.api.filter_by_date',

    auto: true, // required, since it should start fetching automatically
    cache: 'filter_livestatus',
    method: 'GET',
})


export default filterlivestatus;
