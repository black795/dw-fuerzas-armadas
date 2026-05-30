terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "> 4.23.0"
    }
  }
}

provider "azurerm" {
    features{}
}

# 1. Grupo de Recursos para Fuerzas Armadas
resource "azurerm_resource_group" "rg_ffaa" {
  name     = "gr-sisger-dwffaa-5756067"
  location = "Brazil South"
}

# 2. Almacenamiento (Data Lake Gen2 para Bronze/Silver)
resource "azurerm_storage_account" "sa_ffaa" {
  name                     = "saucbdwffaa5756067"
  resource_group_name      = azurerm_resource_group.rg_ffaa.name
  location                 = azurerm_resource_group.rg_ffaa.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = "true" 
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.sa_ffaa.name
  container_access_type = "blob"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.sa_ffaa.name
  container_access_type = "blob"
}

# 3. Servidor SQL y Base de Datos (Data Warehouse Gold)
resource "azurerm_mssql_server" "db_server_ffaa" {
  name                         = "sql-ucb-sisger-ffaa-5756067"
  resource_group_name          = azurerm_resource_group.rg_ffaa.name
  location                     = azurerm_resource_group.rg_ffaa.location
  version                      = "12.0"
  administrator_login          = "alan"
  administrator_login_password = "S3cur3_P@ssw0rd_2026"
}

resource "azurerm_mssql_firewall_rule" "allow_all_ffaa" {
  name             = "AllowAll"
  server_id        = azurerm_mssql_server.db_server_ffaa.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

resource "azurerm_mssql_database" "dw_ffaa" {
  name         = "dw_ffaa"
  server_id    = azurerm_mssql_server.db_server_ffaa.id
  collation    = "SQL_Latin1_General_CP1_CI_AS"
  license_type = "LicenseIncluded"
  max_size_gb  = 2
  sku_name     = "S0"
}

# 4. Azure Data Factory
resource "azurerm_data_factory" "df_ffaa" {
  name                = "adf-ucb-dw-ffaa-5756067"
  location            = azurerm_resource_group.rg_ffaa.location
  resource_group_name = azurerm_resource_group.rg_ffaa.name
}

resource "azurerm_data_factory_linked_service_azure_sql_database" "ls_sqldb" {
  name                = "ls_sqldb_gold"
  data_factory_id     = azurerm_data_factory.df_ffaa.id
  connection_string   = "Integrated Security=False;Data Source=sql-ucb-sisger-ffaa-5756067.database.windows.net;Initial Catalog=dw_ffaa;User ID=alan;Password=S3cur3_P@ssw0rd_2026"
}

resource "azurerm_data_factory_dataset_azure_sql_table" "ds_dim_tiempo" {
  name                = "ds_gold_dim_tiempo"
  data_factory_id     = azurerm_data_factory.df_ffaa.id
  linked_service_id   = azurerm_data_factory_linked_service_azure_sql_database.ls_sqldb.id
  schema              = "gold"
  table               = "dim_tiempo"
}

resource "azurerm_data_factory_dataset_azure_sql_table" "ds_dim_unidad" {
  name                = "ds_gold_dim_unidad"
  data_factory_id     = azurerm_data_factory.df_ffaa.id
  linked_service_id   = azurerm_data_factory_linked_service_azure_sql_database.ls_sqldb.id
  schema              = "gold"
  table               = "dim_unidad"
}

resource "azurerm_data_factory_dataset_azure_sql_table" "ds_hechos_operacion" {
  name                = "ds_gold_hechos_operacion"
  data_factory_id     = azurerm_data_factory.df_ffaa.id
  linked_service_id   = azurerm_data_factory_linked_service_azure_sql_database.ls_sqldb.id
  schema              = "gold"
  table               = "hechos_operacion"
}

resource "azurerm_data_factory_pipeline" "pipeline_etl" {
  name            = "pl_bronze_to_gold_etl"
  data_factory_id = azurerm_data_factory.df_ffaa.id

  activities_json = <<JSON
  [
    {
      "name": "SP_Bronze_to_Silver",
      "type": "SqlServerStoredProcedure",
      "linkedServiceName": {
        "referenceName": "ls_sqldb_gold",
        "type": "LinkedServiceReference"
      },
      "typeProperties": {
        "storedProcedureName": "[silver].[sp_bronze_to_silver]"
      }
    },
    {
      "name": "SP_Silver_to_Gold",
      "type": "SqlServerStoredProcedure",
      "dependsOn": [
        {
          "activity": "SP_Bronze_to_Silver",
          "dependencyConditions": ["Succeeded"]
        }
      ],
      "linkedServiceName": {
        "referenceName": "ls_sqldb_gold",
        "type": "LinkedServiceReference"
      },
      "typeProperties": {
        "storedProcedureName": "[gold].[sp_silver_to_gold]"
      }
    }
  ]
JSON
}