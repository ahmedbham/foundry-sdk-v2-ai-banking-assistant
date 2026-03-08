targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment (used to generate resource names)')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the Foundry account')
param foundryAccountName string = ''

@description('Name of the Foundry project')
param foundryProjectName string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

var actualFoundryAccountName = !empty(foundryAccountName) ? foundryAccountName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
var actualFoundryProjectName = !empty(foundryProjectName) ? foundryProjectName : '${environmentName}-project'

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

module foundry './modules/foundry.bicep' = {
  name: 'foundry'
  scope: rg
  params: {
    location: location
    foundryAccountName: actualFoundryAccountName
    foundryProjectName: actualFoundryProjectName
    tags: tags
  }
}

module acr './modules/acr.bicep' = {
  name: 'acr'
  scope: rg
  params: {
    location: location
    registryName: '${abbrs.containerRegistries}${resourceToken}'
    tags: tags
  }
}

module containerApps './modules/container-apps.bicep' = {
  name: 'container-apps'
  scope: rg
  params: {
    location: location
    environmentName: environmentName
    tags: tags
    projectEndpoint: foundry.outputs.projectEndpoint
    acrLoginServer: acr.outputs.loginServer
    acrName: acr.outputs.name
    foundryAccountName: actualFoundryAccountName
  }
}

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = acr.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = acr.outputs.name
output PROJECT_ENDPOINT string = foundry.outputs.projectEndpoint
output BACKEND_FQDN string = containerApps.outputs.backendFqdn
output MIDDLE_TIER_FQDN string = containerApps.outputs.middleTierFqdn
output FRONTEND_FQDN string = containerApps.outputs.frontendFqdn
