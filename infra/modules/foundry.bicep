@description('Location for resources')
param location string

@description('Foundry account name')
param foundryAccountName string

@description('Foundry project name')
param foundryProjectName string

@description('Tags for resources')
param tags object = {}

resource foundry 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' = {
  name: foundryAccountName
  location: location
  tags: tags
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: foundryAccountName
    publicNetworkAccess: 'Enabled'
    allowProjectManagement: true
  }

  resource project 'projects' = {
    name: foundryProjectName
    location: location
    tags: tags
    identity: {
      type: 'SystemAssigned'
    }
    properties: {}
  }

  resource model 'deployments' = {
    name: 'agent-model'
    sku: {
      capacity: 1
      name: 'GlobalStandard'
    }
    properties: {
      model: {
        format: 'OpenAI'
        name: 'gpt-4.1'
        version: '2025-04-14'
      }
      raiPolicyName: 'Microsoft.DefaultV2'
    }
  }
}

output projectEndpoint string = 'https://${foundry.properties.endpoint}/'
