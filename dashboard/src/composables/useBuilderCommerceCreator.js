let builderCommerceHost = null

export function registerBuilderCommerceHost(host) {
  builderCommerceHost = host
  return () => {
    if (builderCommerceHost === host) builderCommerceHost = null
  }
}

export function requestBuilderProductCreation(onCreated) {
  builderCommerceHost?.openProduct(onCreated)
}

export function requestBuilderCategoryCreation(onCreated) {
  builderCommerceHost?.openCategory(onCreated)
}

export function requestBuilderBrandCreation(onCreated) {
  builderCommerceHost?.openBrand(onCreated)
}
