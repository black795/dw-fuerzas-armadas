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

  github_configuration {
    account_name    = "black795"
    branch_name     = "master"
    repository_name = "dw-fuerzas-armadas"
    root_folder     = "/"
  }
}