@description('Location for resources')
param location string

@description('Environment name')
param environmentName string

@description('Tags for resources')
param tags object = {}

@description('Foundry project endpoint')
param projectEndpoint string

@description('ACR login server')
param acrLoginServer string

@description('ACR name')
param acrName string

var abbrs = loadJsonContent('../abbreviations.json')

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${abbrs.containerAppsEnvironments}logs-${environmentName}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${abbrs.containerAppsEnvironments}${environmentName}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

resource backend 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${abbrs.containerApps}backend-${environmentName}'
  location: location
  tags: union(tags, { 'azd-service-name': 'backend' })
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      registries: [
        {
          server: acrLoginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
      ingress: {
        external: false
        targetPort: 8000
      }
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: 'mcr.microsoft.com/azurelinux/base/nginx:1.25'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

resource middleTier 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${abbrs.containerApps}middle-${environmentName}'
  location: location
  tags: union(tags, { 'azd-service-name': 'middle-tier' })
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      registries: [
        {
          server: acrLoginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
      ingress: {
        external: false
        targetPort: 8001
      }
    }
    template: {
      containers: [
        {
          name: 'middle-tier'
          image: 'mcr.microsoft.com/azurelinux/base/nginx:1.25'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'PROJECT_ENDPOINT'
              value: projectEndpoint
            }
            {
              name: 'MODEL_DEPLOYMENT_NAME'
              value: 'agent-model'
            }
            {
              name: 'BACKEND_URL'
              value: 'https://${backend.properties.configuration.ingress.fqdn}'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

resource frontend 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${abbrs.containerApps}frontend-${environmentName}'
  location: location
  tags: union(tags, { 'azd-service-name': 'frontend' })
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      registries: [
        {
          server: acrLoginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
      ingress: {
        external: true
        targetPort: 80
      }
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: 'mcr.microsoft.com/azurelinux/base/nginx:1.25'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'VITE_CHAT_API_URL'
              value: 'https://${middleTier.properties.configuration.ingress.fqdn}'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output backendFqdn string = backend.properties.configuration.ingress.fqdn
output middleTierFqdn string = middleTier.properties.configuration.ingress.fqdn
output frontendFqdn string = frontend.properties.configuration.ingress.fqdn
