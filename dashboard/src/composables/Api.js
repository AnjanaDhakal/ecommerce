import { ref } from 'vue'



  export default function useApi() {
    const vendorData = ref([])
    const error = ref(null)

    // Get All Branch Data
    const getAllBranch = async () => {
      vendorData.value = []
      error.value = null
      try {
        const response = await fetch(`/api/resource/Ecommerce%20Branch?fields=["name","branch_name","branch_description","branch_code","branch_type"]`)
        const data = await response.json()
      //  // console.log(data.data)
        vendorData.value = data.data
      } catch (err) {
        error.value = err
      }
    }


    // Get all Order
    const getAllOrder = async () => {
      vendorData.value = []
      error.value = null
      try {
        const response = await fetch(` api/resource/Ecommerce%20Vendor%20Order?fields=[ "name",
        "customer_name",
        "primary_mobile_no",
        "secondary_mobile_no",
        "location",
        "delivery_amount",
        "cod_amount",
        "status",
        "vendor_tracking_number",
        "order_description",
        "creation",
        "pickup_branch",
        "destination_branch",
        "name_of_city_area",
        "failed_attempt",
        "pickup",
        "vendor_address",
        "previous_warehouse",
        "current_warehouse",
        "dispatch_status",
        "paid_to_vendor",
        "final_cod_amount",
        "final_delivery_charge",
        "order_description",
        "instruction",
        "is_paid_order",
        "order_type"]&order_by=creation%20desc"`)
        const data = await response.json()
      //  //console.log("ukdff",data)
       vendorData.value = data.data
      } catch (err) {
        error.value = err
      }
    }

        // Get All comment Data
        const getAllComments = async () => {
          vendorData.value = []
          error.value = null
          try {
            const response = await fetch(`/api/resource/Comment?fields=["name", "comment_email", "content", "creation"]&order_by=creation%20desc"`)
            const data = await response.json()
          //  // console.log(data.data)
            vendorData.value = data.data
          } catch (err) {
            error.value = err
          }
        }




    return {
      vendorData,
      error,
      getAllBranch,
      getAllOrder,
      getAllComments

    }
  }
