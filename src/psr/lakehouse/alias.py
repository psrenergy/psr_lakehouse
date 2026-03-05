"""Auto-generated table alias methods for the PSR Lakehouse Client.

DO NOT EDIT — regenerate with: make generate-aliases
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def aneel_distributed_generation_projects(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **aneel_distributed_generation_projects** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **aneel_upload_date** *string (date)* — Date when the dataset was generated (DatGeracaoConjuntoDados)
    - **aneel_upload_period** *string (date)* — Reference period as first day of month (AnmPeriodoReferencia)
    - **distributor_cnpj** *string* — CNPJ of the distribution company (NumCNPJDistribuidora)
    - **distributor_code** *string* — Distribution company abbreviation code (CodAgente)
    - **distributor_name** *string* — Distribution company name (NomAgente)
    - **consumer_class_code** *string* — Consumer class code (CodClasseConsumo)
    - **consumer_class_description** *string* — Consumer class description (DscClasseConsumo)
    - **tariff_subgroup** *enum* — Tariff subgroup (DscSubGrupoTarifario) ['A1', 'A2', 'A3', 'A3a', 'A4', 'AS', 'B1', 'B2', 'B3', 'B4']
    - **state_ibge_code** *string* — IBGE state code (CodUFibge)
    - **state_code** *enum* — State abbreviation (SigUF) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **region_code** *string* — Region code (CodRegiao)
    - **region** *enum* — Region name (NomRegiao) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'CENTRO-OESTE']
    - **municipality_ibge_code** *string* — IBGE municipality code (CodMunicipioIbge)
    - **municipality_name** *string* — Municipality name (NomMunicipio)
    - **postal_code** *string* — CEP/postal code (CodCEP)
    - **consumer_type** *enum* — Type of consumer: Individual (PF) or Legal Entity (PJ) (TipoConsumidor) ['PF', 'PJ']
    - **owner_cpf_cnpj** *string* — CPF or CNPJ of the project owner (NumCPFCNPJ)
    - **owner_name** *string* — Name of the project owner (NomTitularEmpreendimento)
    - **project_code** *string* — Unique project code (CodEmpreendimento)
    - **project_updated_at** *string* — Date of last cadastral update for the project (DthAtualizaCadastralEmpreend)
    - **project_modality_description** *string* — Description of the enabled modality (DscModalidadeHabilitado)
    - **credit_receiving_units_count** *integer* — Number of consumer units receiving credits (QtdUCRecebeCredito)
    - **generation_type_code** *enum* — Code of the generation type (SigTipoGeracao) ['UTN', 'UTE', 'UHE', 'UFV', 'EOL', 'PCH', 'CGH']
    - **generation_source_description** *string* — Description of the generation source (DscFonteGeracao)
    - **project_type** *enum* — Description of the project size: Microgeneration or Minigeneration (DscPorteEmpreendimento) ['MICROGERACAO', 'MINIGERACAO']
    - **installed_capacity_kw** *number* — Installed capacity in kW (MdaPotenciaInstaladaKW)
    - **project_latitude** *number* — Latitude coordinate of the project (NumCoordNEmpreendimento)
    - **project_longitude** *number* — Longitude coordinate of the project (NumCoordEEmpreendimento)
    - **substation_name** *string* — Name of the substation (NomSubEstacao)
    - **substation_longitude** *number* — Longitude coordinate of the substation (NumCoordESub)
    - **substation_latitude** *number* — Latitude coordinate of the substation (NumCoordNSub)
    - **modality_type** *enum* — Simplified categorization of project modality (DscModalidadeHabilitado) ['LOCAL', 'REMOTE_SELF_CONSUMPTION', 'SHARED_GENERATION']
    - **average_capacity_per_credit_unit_kw** *number* — Average installed capacity per credit-receiving unit (installed_capacity_kw / credit_receiving_units_count)
    """
    return self.fetch_dataframe(table_name="aneel_distributed_generation_projects", **kwargs)


def ccee_spot_price(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ccee_spot_price** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **spot_price** *number* — Spot price in R$/MWh
    - **reference_date** *string (date-time)* — Timestamp of the spot price
    - **subsystem** *enum* — Subsystem of the spot price ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    """
    return self.fetch_dataframe(table_name="ccee_spot_price", **kwargs)


def ccee_spot_price_average_monthly(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ccee_spot_price_average_monthly** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **average_spot_price** *number* — Average spot price in R$/MWh
    - **reference_date** *string (date)* — Reference month of the average spot price
    - **subsystem** *enum* — Subsystem of the average spot price ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    """
    return self.fetch_dataframe(table_name="ccee_spot_price_average_monthly", **kwargs)


def ccee_spot_price_historical_weekly(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ccee_spot_price_historical_weekly** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **spot_price** *number* — Spot price in R$/MWh (PLD_HORA)
    - **reference_date** *string (date-time)* — Timestamp of the spot price (data)
    - **subsystem** *enum* — Subsystem of the spot price (submercado) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **load_block** *enum* — Load block of the spot price (bloco de carga) ['Off-Peak', 'Intermediate', 'Peak']
    """
    return self.fetch_dataframe(table_name="ccee_spot_price_historical_weekly", **kwargs)


def c_e_g(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **c_e_g** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **value** *string* — CEG value
    """
    return self.fetch_dataframe(table_name="c_e_g", **kwargs)


def c_e_g_data(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **c_e_g_data** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **ceg_id** *integer* — Foreign key to the ONS CEG
    - **state_code** *enum* — State ID of the CEG (id_estado) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **technology** *string* — Technology of the CEG (nom_tecnologia)
    - **fuel_type** *string* — Fuel type of the CEG (nom_combustivel)
    - **version** *integer* — Version of the CEG record
    - **source** *string* — Source of the CEG data
    """
    return self.fetch_dataframe(table_name="c_e_g_data", **kwargs)


def e_p_e_energy_consumption_monthly(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **e_p_e_energy_consumption_monthly** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date)* — Reference date of the consumption record (Data)
    - **state_code** *enum* — Brazilian state code (UF) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **region** *enum* — Geographic region of Brazil (Regiao) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'CENTRO-OESTE']
    - **subsystem** *enum* — Subsystem or Isolated Systems (Sistema) ['SISTEMAS ISOLADOS', 'SUDESTE / CENTRO - OESTE', 'NORDESTE', 'NORTE INTERLIGADO', 'SUL']
    - **consumer_class** *enum* — Consumer class (Classe) ['Residencial', 'Industrial', 'Comercial', 'Rural', 'Outros']
    - **consumer_type** *enum* — Consumer type: Captive or Free (TipoConsumidor) ['Cativo', 'Livre']
    - **consumption_mwh** *number* — Energy consumption in MWh (Consumo)
    - **consumers** *integer* — Number of consumer units (Consumidores)
    - **data_version_date** *string* — Data version/update date (DataVersao)
    """
    return self.fetch_dataframe(table_name="e_p_e_energy_consumption_monthly", **kwargs)


def generator_generator_unit(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **generator_generator_unit** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **generator_id** *integer* — Foreign key to the ONS Generator Set
    - **unit_id** *integer* — Foreign key to the GeneratorUnit
    - **relation_start_date** *string* — Start date of the relation between generator set and generator_unit
    - **relation_end_date** *string* — End date of the relation between generator set and generator_unit
    """
    return self.fetch_dataframe(table_name="generator_generator_unit", **kwargs)


def generator_unit(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **generator_unit** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **ons_id** *string* — ONS identifier of the generator unit (id_usina)
    - **equipment_code** *string* — Equipment code of the generator set (cod_equipamento)
    - **ceg_id** *integer* — Foreign key to the ONS CEG
    """
    return self.fetch_dataframe(table_name="generator_unit", **kwargs)


def ons_commercial_generation_international_export(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_commercial_generation_international_export** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Reference date for the data (din_instante).
    - **export_argentina_hydro** *number* — Hydroelectric excedent export to Argentina in MWavg (val_gerexpevt_ar)
    - **export_argentina_total** *number* — Total export to Argentina at conversors Garabi I and Garabi II in MWavg (val_exportacao_ar)
    - **export_uruguay_hydro** *number* — Hydroelectric excedent export to Uruguay in MWavg (val_gerexpevt_uy)
    - **export_uruguay_total** *number* — Total export to Uruguay at conversors Rivero and Melo in MWavg (val_exportacao_uy)
    - **export_thermal** *number* — Thermal generation export in MWavg (val_gerexptermica)
    """
    return self.fetch_dataframe(table_name="ons_commercial_generation_international_export", **kwargs)


def ons_controlled_power_flow_program_daily(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_controlled_power_flow_program_daily** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'RORAIMA']
    - **reference_date** *string (date-time)* — Reference date (din_programacaodia)
    - **level** *integer* — Level number (num_patamar)
    - **element_name** *string* — Name of the controlled energy flow element (nom_elementofluxocontrolado)
    - **element_description** *string* — Description of the controlled energy flow element (dsc_elementofluxocontrolado)
    - **terminal_type** *integer* — Type of terminal (tip_terminal)
    - **load_value** *number* — Scheduled load value in MWavg (val_carga)
    """
    return self.fetch_dataframe(table_name="ons_controlled_power_flow_program_daily", **kwargs)


def ons_energy_balance_subsystem(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_energy_balance_subsystem** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **reference_date** *string (date-time)* — Reference date (din_instante)
    - **generation_hydraulic** *number* — Verified hydraulic generation in MWavg (val_gerhidraulica)
    - **generation_thermal** *number* — Verified thermal generation in MWavg (val_gertermica)
    - **generation_wind** *number* — Verified wind generation in MWavg (val_gereolica)
    - **generation_solar** *number* — Verified solar generation in MWavg (val_gersolar)
    - **load** *number* — Verified load in MWavg (val_carga)
    - **net_interchange** *number* — Verified net interchange in MWavg (val_intercambio)
    """
    return self.fetch_dataframe(table_name="ons_energy_balance_subsystem", **kwargs)


def ons_energy_import_commercial_block(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_energy_import_commercial_block** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Reference timestamp for the energy import (din_instante).
    - **origin_country** *enum* — Country of origin for the energy import (nom_pais). ['ARGENTINA', 'URUGUAI']
    - **agent_name** *string* — Name of the agent responsible for the energy import (nom_agente).
    - **block_name** *string* — Name of the import block (nom_bloco).
    - **programmed_import** *number* — Programmed energy import in MWh (val_importacaoprogramada).
    - **dispatched_import** *number* — Dispatched energy import in MWh (val_importacaodespachada).
    - **verified_import** *number* — Verified energy import in MWh (val_importacaoverificada).
    - **price** *number* — Price of the imported energy in R$/MWh (val_preco).
    """
    return self.fetch_dataframe(table_name="ons_energy_import_commercial_block", **kwargs)


def ons_energy_import_price_bids(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_energy_import_price_bids** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **start_date** *string (date-time)* — Start date for the data (dat_iniciovalidade).
    - **end_date** *string (date-time)* — End date for the data (dat_fimvalidade).
    - **origin_country** *enum* — Country of origin of the energy (nom_pais). ['ARGENTINA', 'URUGUAI']
    - **agent_name** *string* — Agent name (nom_agente).
    - **block_name** *string* — Block name (nom_bloco).
    - **price** *number* — Price of the energy in R$/MWh (val_preco).
    """
    return self.fetch_dataframe(table_name="ons_energy_import_price_bids", **kwargs)


def ons_energy_load_daily(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_energy_load_daily** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date)* — Date of the energy load record
    - **subsystem** *enum* — Subsystem of the stored energy ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **energy_load** *number* — Daily energy load in the subsystem in MWavg (val_cargaenergiamwmed)
    """
    return self.fetch_dataframe(table_name="ons_energy_load_daily", **kwargs)


def ons_energy_load_monthly(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_energy_load_monthly** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date)* — Date of the energy load record
    - **subsystem** *enum* — Subsystem of the stored energy ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **energy_load** *number* — Monthly energy load in the subsystem in MWavg (val_cargaenergiamwmed)
    """
    return self.fetch_dataframe(table_name="ons_energy_load_monthly", **kwargs)


def ons_energy_load_verified(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_energy_load_verified** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **load_area_code** *enum* — Load area code (cod_areacarga) ['SECO', 'S', 'NE', 'N', 'PESE', 'PES', 'PENE', 'PEN', 'RJ', 'SP', 'MG', 'ES', 'MT', 'MS', 'DF', 'GO', 'AC', 'RO', 'PR', 'SC', 'RS', 'BASE', 'BAOE', 'ALPE', 'PBRN', 'CE', 'PI', 'TON', 'PA', 'MA', 'AP', 'AM', 'RR']
    - **date_of_reference** *string (date)* — Date of reference (dat_referencia)
    - **reference_date** *string (date-time)* — Reference date at the end of the half-hour interval in UTC+0h timezone (din_referenciautc)
    - **global_load** *number* — Global load value in MWmed integrated at the end of the half-hour interval (val_cargaglobal)
    - **global_load_net_mmgd** *number* — Global load net of MMGD in MWmed integrated at the end of the half-hour interval (val_cargaglobalsmmgd)
    - **mmgd_load** *number* — Load served by MMGD in MWmed integrated at the end of the half-hour interval (val_cargammgd)
    - **global_load_consistent** *number* — Consistent global load in MWmed integrated at the end of the half-hour interval (val_cargaglobalcons)
    - **consistency_value** *number* — Consistency value in MWmed integrated at the end of the half-hour interval (val_consistencia)
    - **supervised_load** *number* — Load supervised by ONS (generation type I, IIA, IIB, IIC and interchanges) in MWmed integrated at the end of the half-hour interval (val_cargasupervisionada)
    - **unsupervised_load** *number* — Load not supervised by ONS, from CCEE billing measurement system (generation type III) in MWmed integrated at the end of the half-hour interval (val_carganaosupervisionada)
    """
    return self.fetch_dataframe(table_name="ons_energy_load_verified", **kwargs)


def ons_exchange_international(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_exchange_international** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **destination_country** *enum* — Destination country of energy exchange (nom_paisdestino) ['ARGENTINA', 'URUGUAI']
    - **reference_date** *string (date-time)* — Reference date and time of the energy exchange measurement (din_instante)
    - **exchange** *number* — Verified exchange in hourly basis in MWavg (val_intercambiomwmed). Positive values indicate export, negative values indicate import
    """
    return self.fetch_dataframe(table_name="ons_exchange_international", **kwargs)


def ons_exchange_modality(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_exchange_modality** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **converter** *string* — Converter name (nom_conversora).
    - **reference_date** *string (date-time)* — Reference date and time of the energy exchange measurement (din_instante)
    - **val_contract** *number* — Value of exported energy in contractual modality in MWmed (val_modalidadecontratual).
    - **val_emergency** *number* — Value of exported energy in emergency modality in MWmed (val_modalidadeemergencial).
    - **val_opportunity** *number* — Value of exported energy in opportunity modality in MWmed (val_modalidadeoportunidade).
    - **val_test** *number* — Value of exported energy in test modality in MWmed (val_modalidadeteste).
    - **val_exceptional** *number* — Value of exported energy in exceptional modality in MWmed (val_modalidadeexcepcional).
    """
    return self.fetch_dataframe(table_name="ons_exchange_modality", **kwargs)


def ons_exchange_subsystem(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_exchange_subsystem** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **subsystem_from** *enum* — Subsystem from (nom_subsistema_origem) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **subsystem_to** *enum* — Subsystem to (nom_subsistema_destino) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **reference_date** *string (date-time)* — Reference date and time of the energy exchange measurement (din_instante)
    - **exchange** *number* — Verified exchange in hourly basis in MWmed (val_intercambiomwmed). Positive values indicate export, negative values indicate import
    """
    return self.fetch_dataframe(table_name="ons_exchange_subsystem", **kwargs)


def ons_generator_data(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_generator_data** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **generator_id** *integer* — Foreign key to the ONS Generator Set
    - **ons_set_id** *string* — Unique identifier of the generator set (id_ons_usina, id_ons_pequenasusinas)
    - **plant_set_id** *integer* — Code of the generator set (id_conjuntousina)
    - **name** *string* — Name of the generator set (nom_usina)
    - **state_code** *enum* — State ID of the generator set (id_estado - Installed Capacity) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **subsystem** *enum* — Subsystem of the generator set (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **operation_mode** *enum* — Operation mode of the generator set (nom_modalidadeoperacao) ['TIPO I', 'TIPO II-A', 'TIPO II-B', 'TIPO II-C', 'TIPO III', 'MMGD']
    - **proprietary_agent** *string* — Proprietary agent of the generator set (nom_agenteproprietario)
    - **operator_agent** *string* — Operator agent of the generator set (nom_agenteoperador)
    - **plant_type** *enum* — Type of the plant (nom_tipousina) ['HIDROELÉTRICA', 'TÉRMICA', 'EOLIELÉTRICA', 'FOTOVOLTAICA', 'NUCLEAR', 'BOMBEAMENTO']
    - **fuel_type** *string* — Fuel type of the generator set (nom_combustivel)
    """
    return self.fetch_dataframe(table_name="ons_generator_data", **kwargs)


def ons_generator_unit_data(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_generator_unit_data** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **name** *string* — Name of the generator unit (nom_usina)
    - **unit_id** *integer* — Foreign key to the ONS Power Plant
    - **aneel_status** *enum* — ANEEL status of the generator unit (sts_aneel) ['A', 'I', 'C', 'F', 'O']
    - **operation_center_code** *string* — Operation center code of the generator unit (sgl_centrooperacao)
    - **authorized_capacity** *number* — Authorized capacity of the generator unit in MW (val_potenciaautorizada)
    - **connection_point** *string* — Connection point of the generator unit (nom_pontoconexao)
    - **generator_unit_name** *string* — Name of the generator unit (nom_unidadegeradora)
    - **generator_unit_number** *string* — Number of the generator unit (num_unidadegeradora)
    - **commissioning_date** *string* — Commissioning date of the generator set (dat_entradateste)
    - **operation_date** *string* — Comercial Operation date of the generator set (dat_entradaoperacao)
    - **decommissioning_date** *string* — Decommissioning date of the generator set (dat_desativacao)
    - **nominal_capacity** *number* — Nominal capacity of the generator set in MW (val_potenciaefetiva)
    - **is_active** *boolean* — Indicates if the generator unit is currently active on ONS records
    """
    return self.fetch_dataframe(table_name="ons_generator_unit_data", **kwargs)


def ons_hydrological_reservoir_data_daily(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_hydrological_reservoir_data_daily** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Reference date for the data (din_instante).
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **reservoir_type** *enum* — Type of the reservoir (tip_reservatorio) ['FIO', 'RCU', 'RES', 'CED', 'FIC', 'RBB']
    - **basin_name** *string* — Name of the basin (nom_bacia)
    - **equivalent_reservoir_name** *string* — Name of the equivalent reservoir (nom_ree)
    - **reservoir_id** *string* — Reservoir ID (id_reservatorio)
    - **reservoir_name** *string* — Name of the reservoir (nom_reservatorio)
    - **reservoir_cascade_order** *number* — Reservoir order in the cascade (num_ordemcs)
    - **plant_code** *number* — Plant code (cod_usina)
    - **upstream_level** *number* — Upstream level in meters (val_nivelmontante)
    - **downstream_level** *number* — Downstream level in meters (val_niveljusante)
    - **usable_storage_volume_percentage** *number* — Usable storage volume in percentage (%) (val_volumeutilcon)
    - **inflow_rate** *number* — Inflow rate (m3/s) (val_vazaoafluente)
    - **flow_rate_turbined** *number* — Turbined flow rate (m3/s) (val_vazaoturbinada)
    - **flow_rate_spilled** *number* — Spilled flow rate (m3/s) (val_vazaovertida)
    - **flow_rate_other_structures** *number* — The flow returned to the river downstream of the plant through pathways other than the spillway or generating units' turbines (m3/s) (val_vazaooutrasestruturas)
    - **total_outflow_rate** *number* — Total outflow rate from the reservoir, accounting for the turbined flow rate, the flow rate from other structures and the spilled flow rate (m3/s) (val_vazaodefluente)
    - **flow_rate_transferred** *number* — Transferred flow rate to and from another reservoir (m3/s) (val_vazaotransferida)
    - **flow_rate_natural** *number* — Natural flow rate (m3/s) (val_vazaonatural)
    - **flow_rate_artificial** *number* — Artificial flow rate (m3/s) (val_vazaoartificial)
    - **flow_rate_incremental** *number* — Flow resulting from the contribution between two measurement points (m3/s) (val_vazaoincremental)
    - **flow_rate_net_evaporation** *number* — Net evaporation flow rate (m3/s) (val_vazaoevaporacaoliquida)
    - **flow_rate_consumptive_use** *number* — Consumptive use flow rate (m3/s) (val_vazaousoconsuntivo)
    - **flow_rate_gross_incremental** *number* — Gross incremental flow rate (m3/s) (val_vazaoincrementalbruta)
    """
    return self.fetch_dataframe(table_name="ons_hydrological_reservoir_data_daily", **kwargs)


def ons_hydrological_reservoir_data_hourly(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_hydrological_reservoir_data_hourly** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Reference date for the data (din_instante).
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **reservoir_type** *enum* — Type of the reservoir (tip_reservatorio) ['FIO', 'RCU', 'RES', 'CED', 'FIC', 'RBB']
    - **basin_name** *string* — Name of the basin (nom_bacia)
    - **reservoir_id** *string* — Reservoir ID (id_reservatorio)
    - **reservoir_name** *string* — Name of the reservoir (nom_reservatorio)
    - **plant_code** *number* — Plant code (cod_usina)
    - **upstream_level** *number* — Upstream water level in meters (val_nivelmontante)
    - **downstream_level** *number* — Downstream water level in meters (val_niveljusante)
    - **usable_storage_volume_percentage** *number* — Usable storage volume in percentage (%) (val_volumeutil)
    - **inflow_rate** *number* — Inflow rate (m3/s) (val_vazaoafluente)
    - **flow_rate_turbined** *number* — Turbined flow rate (m3/s) (val_vazaoturbinada)
    - **flow_rate_spilled** *number* — Spilled flow rate (m3/s) (val_vazaovertida)
    - **flow_rate_other_structures** *number* — The flow returned to the river downstream of the plant through pathways other than the spillway or generating units' turbines (m3/s) (val_vazaooutrasestruturas)
    - **total_outflow_rate** *number* — Total outflow rate from the reservoir, accounting for the turbined flow rate, the flow rate from other structures and the spilled flow rate (m3/s) (val_vazaodefluente)
    - **flow_rate_transferred** *number* — Transferred flow rate to and from another reservoir (m3/s) (val_vazaotransferida)
    - **flow_rate_non_turbinable_spill** *number* — Non-turbinable spill flow rate (m3/s) (val_vazaovertidanaoturbinavel)
    """
    return self.fetch_dataframe(table_name="ons_hydrological_reservoir_data_hourly", **kwargs)


def ons_inflow_energy_basin(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_inflow_energy_basin** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **basin_name** *string* — Name of the basin (nom_bacia)
    - **reference_date** *string (date)* — Reference date of the inflow energy measurement (ena_data)
    - **gross_inflow_energy_mwavg** *number* — Gross inflow energy in MWavg (ena_bruta_bacia_mwmed)
    - **gross_inflow_energy_percentage_mlt** *number* — Gross inflow energy as percentage of Long-term Average (MLT) (ena_bruta_bacia_percentualmlt)
    - **storable_inflow_energy_mwavg** *number* — Storable inflow energy in MWavg (ena_armazenavel_bacia_mwmed)
    - **storable_inflow_energy_percentage_mlt** *number* — Storable inflow energy as percentage of Long-term Average (MLT) (ena_armazenavel_bacia_percentualmlt)
    """
    return self.fetch_dataframe(table_name="ons_inflow_energy_basin", **kwargs)


def ons_inflow_energy_equivalent_reservoir(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_inflow_energy_equivalent_reservoir** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **ree_name** *string* — Name of the REE (Equivalent Energy Reservoir) (nom_reservatorioee)
    - **reference_date** *string (date)* — Reference date of the inflow energy measurement (ena_data)
    - **gross_inflow_energy_mwavg** *number* — Gross inflow energy in average MW (ena_bruta_ree_mwmed)
    - **gross_inflow_energy_percentage_mlt** *number* — Gross inflow energy as percentage of Long-term Average(MLT) (ena_bruta_ree_percentualmlt)
    - **storable_inflow_energy_mwavg** *number* — Storable inflow energy in average MW (ena_armazenavel_ree_mwmed)
    - **storable_inflow_energy_percentage_mlt** *number* — Storable inflow energy as percentage of Long-term average (MLT) (ena_armazenavel_ree_percentualmlt)
    """
    return self.fetch_dataframe(table_name="ons_inflow_energy_equivalent_reservoir", **kwargs)


def ons_inflow_energy_reservoir(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_inflow_energy_reservoir** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reservoir_name** *string* — Name of the reservoir (nom_reservatorio)
    - **planning_code** *number* — Planning code of the reservoir (cod_resplanejamento)
    - **reservoir_type** *enum* — Type of reservoir (tip_reservatorio) ['FIO', 'RCU', 'RES', 'CED', 'FIC', 'RBB']
    - **basin_name** *string* — Name of the basin (nom_bacia)
    - **equivalent_reservoir** *string* — Name of the equivalent reservoir (nom_ree)
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **reference_date** *string (date)* — Reference date of the inflow energy measurement (ena_data)
    - **gross_inflow_energy_mwavg** *number* — Gross inflow energy in MWavg (ena_bruta_res_mwmed)
    - **gross_inflow_energy_percentage_mlt** *number* — Gross inflow energy as percentage of Long-term Average (MLT) (ena_bruta_res_percentualmlt)
    - **storable_inflow_energy_mwavg** *number* — Storable inflow energy in MWavg (ena_armazenavel_res_mwmed)
    - **storable_inflow_energy_percentage_mlt** *number* — Storable inflow energy as percentage of Long-term Average (MLT) (ena_armazenavel_res_percentualmlt)
    - **gross_head** *number* — Gross inflow energy by head (ena_queda_bruta)
    - **mlt_inflow_energy** *number* — Long-term average(MLT) inflow energy (mlt_ena)
    """
    return self.fetch_dataframe(table_name="ons_inflow_energy_reservoir", **kwargs)


def ons_inflow_energy_subsystem(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_inflow_energy_subsystem** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **reference_date** *string (date)* — Reference date of the inflow energy measurement (ena_data)
    - **gross_inflow_energy_mwavg** *number* — Gross inflow energy in average MW (ena_bruta_regiao_mwmed)
    - **gross_inflow_energy_percentage_mlt** *number* — Gross inflow energy as percentage of MLT (ena_bruta_regiao_percentualmlt)
    - **storable_inflow_energy_mwavg** *number* — Storable inflow energy in average MW (ena_armazenavel_regiao_mwmed)
    - **storable_inflow_energy_percentage_mlt** *number* — Storable inflow energy as percentage of MLT (ena_armazenavel_regiao_percentualmlt)
    """
    return self.fetch_dataframe(table_name="ons_inflow_energy_subsystem", **kwargs)


def ons_load_curve(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_load_curve** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **reference_date** *string (date-time)* — Reference date (din_instante)
    - **energy_load** *number* — Energy load in MWavg (val_cargaenergiahomwmed)
    """
    return self.fetch_dataframe(table_name="ons_load_curve", **kwargs)


def ons_load_marginal_cost_semi_hourly(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_load_marginal_cost_semi_hourly** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **reference_date** *string (date-time)* — Reference date (din_instante)
    - **marginal_cost** *number* — Load marginal cost (CMO) in R$/MWh (val_cmo)
    """
    return self.fetch_dataframe(table_name="ons_load_marginal_cost_semi_hourly", **kwargs)


def ons_load_marginal_cost_weekly(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_load_marginal_cost_weekly** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **average** *number* — Average load marginal cost in the subsystem in R$/MW
    - **light_load_segment** *number* — Light load segment in the subsystem in R$/MW
    - **medium_load_segment** *number* — Medium load segment in the subsystem in R$/MW
    - **heavy_load_segment** *number* — Heavy load segment in the subsystem in R$/MW
    - **reference_date** *string (date)* — Timestamp of the stored energy
    - **subsystem** *enum* — Subsystem of the stored energy ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    """
    return self.fetch_dataframe(table_name="ons_load_marginal_cost_weekly", **kwargs)


def ons_power_plant_availability(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_power_plant_availability** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Timestamp of the stored energy
    - **subsystem** *enum* — Subsystem of the stored energy ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **state_code** *enum* — State ID of the generator (id_estado - Installed Capacity) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **plant_type** *enum* — Type of the plant (nom_tipousina) ['HIDROELÉTRICA', 'TÉRMICA', 'EOLIELÉTRICA', 'FOTOVOLTAICA', 'NUCLEAR', 'BOMBEAMENTO']
    - **fuel_type** *string* — Fuel type of the generator (nom_tipocombustivel)
    - **generator_name** *string* — Name of the generator (nom_usina)
    - **ons_id** *string* — ONS ID of the generator (id_ons)
    - **ceg** *string* — ONS CEG ID of the generator (ceg)
    - **installed_capacity** *number* — Installed capacity of the power plant considered for availability calculation, in MW (val_potenciainstalada)
    - **operational_availability** *number* — Operational availability of the plant, in MW (val_dispoperacional)
    - **synchronized_availability** *number* — Operational availability of the plant, considering only generating units synchronized to the National Integrated System (SIN), in MW (val_dispsincronizada)
    """
    return self.fetch_dataframe(table_name="ons_power_plant_availability", **kwargs)


def ons_power_plant_hourly_generation(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_power_plant_hourly_generation** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Timestamp of the stored energy
    - **subsystem** *enum* — Subsystem of the stored energy ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **state_code** *enum* — State ID of the generator set (id_estado - Installed Capacity) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **operation_mode** *enum* — Operation mode of the generator set (nom_modalidadeoperacao) ['TIPO I', 'TIPO II-A', 'TIPO II-B', 'TIPO II-C', 'TIPO III', 'MMGD']
    - **plant_type** *enum* — Type of the plant (nom_tipousina) ['HIDROELÉTRICA', 'TÉRMICA', 'EOLIELÉTRICA', 'FOTOVOLTAICA', 'NUCLEAR', 'BOMBEAMENTO']
    - **fuel_type** *string* — Fuel type of the generator set (nom_tipocombustivel)
    - **generator_name** *string* — Name of the generator (nom_usina)
    - **ons_id** *string* — ONS ID of the generator set (id_ons)
    - **ceg** *string* — ONS CEG ID of the generator set (ceg)
    - **generation** *number* — Hourly generation in MWavg (val_geracao)
    """
    return self.fetch_dataframe(table_name="ons_power_plant_hourly_generation", **kwargs)


def ons_solar_curtailment(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_solar_curtailment** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Timestamp of the stored energy
    - **subsystem** *enum* — Subsystem ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **state_code** *enum* — State ID of the generator set (id_estado - Installed Capacity) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **generator_name** *string* — Name of the generator (nom_usina)
    - **ons_id** *string* — ONS ID of the generator set (id_ons)
    - **ceg** *string* — ONS CEG ID of the generator set (ceg)
    - **generation** *number* — Generated energy in MWh (val_geracao) / 2
    - **limited_generation** *number* — Limited generation in MWh (val_geracaolimitada) / 2
    - **generation_availability** *number* — Generation availability in MWh (val_disponibilidade) / 2
    - **generation_reference** *number* — Generation reference in MWh (val_geracaoreferencia) / 2
    - **generation_final_reference** *number* — Final generation reference in MWh (val_geracaoreferenciafinal) / 2
    - **reason_code** *enum* — Curtailment reason code (cod_razaorestricao) ['REL', 'CNF', 'ENE', 'PAR']
    - **source_code** *enum* — Curtailment source code (cod_origemrestricao) ['LOC', 'SIS']
    - **description** *string* — Description of the curtailment reason (dsc_restricao)
    - **physical_curtailment** *number* — Physical curtailment in MWh
    - **unconstrained_generation** *number* — Unconstrained generation in MWh (generation + physical_curtailment)
    """
    return self.fetch_dataframe(table_name="ons_solar_curtailment", **kwargs)


def ons_solar_curtailment_detailed(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_solar_curtailment_detailed** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Reference date for the data (din_instante).
    - **subsystem** *enum* — Subsystem identifier. Represents the electrical subsystem within the National Interconnected System (SIN)(sub_sistema). ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **state_code** *enum* — State code. Abbreviation of the state where the plant is located (id_estado). ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **operation_mode** *enum* — Plant operation mode. Indicates the operational modality of the solar plant (nom_modalidadeoperacao). ['TIPO I', 'TIPO II-A', 'TIPO II-B', 'TIPO II-C', 'TIPO III', 'MMGD']
    - **plant_set** *string* — Plant set name. Name of the plant set, applicable only for plants operating under Type II-C modality (nom_conjuntousina).
    - **generator_name** *string* — Generator name. Official name of the solar plant as registered in ONS systems (nom_usina).
    - **ons_id** *string* — ONS plant identifier (id_ons).
    - **ceg** *string* — CEG (ceg).
    - **verified_solar_irradiance** *number* — Verified solar irradiance. Measured solar irradiance data in W/m² at the plant's location (val_irradianciaverificado).
    - **invalid_irradiance_data** *boolean* — Invalid solar irradiance data flag. Indicates whether the solar irradiance measurement is valid due to a monitoring failure lasting more than six minutes within the corresponding half-hour period (flg_dadoirradianciainvalido).
    - **estimated_generation** *number* — Estimated average power generation in MWavg , calculated from the verified solar irradiance data and the solar power curve, or based on historical verified generation if the curve is unavailable (val_geracaoestimada).
    - **verified_generation** *number* — Measured average power generation of the plant in MWavg (val_geracaoverificada).
    """
    return self.fetch_dataframe(table_name="ons_solar_curtailment_detailed", **kwargs)


def ons_spilled_turbinable_energy(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_spilled_turbinable_energy** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Reference date for the data (din_instante).
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **basin_name** *string* — Name of the basin (nom_bacia)
    - **river_name** *string* — Name of the river (nom_rio)
    - **agent_name** *string* — Name of the agent (nom_agente)
    - **reservoir_name** *string* — Name of the reservoir (nom_reservatorio)
    - **plant_code** *number* — Plant code (cod_usina)
    - **generation** *number* — Generated energy in MWavg (val_geracao)
    - **generation_availability** *number* — Generation availability in MWavg (val_disponibilidade)
    - **flow_rate_turbined** *number* — Turbined flow rate (m3/s) (val_vazaoturbinada)
    - **flow_rate_spilled** *number* — Spilled flow rate (m3/s) (val_vazaovertida)
    - **flow_rate_non_turbinable_spill** *number* — Non-turbinable spill flow rate (m3/s) (val_vazaovertidanaoturbinavel)
    - **productivity** *number* — Productivity (MW/m3/s) (val_produtividade)
    - **generation_margin** *number* — Generation margin in MWavg (val_folgadegeracao)
    - **spilled_energy** *number* — Spilled energy in MWavg (val_energiavertida)
    - **spilled_energy_turbinable** *number* — Turbinable spilled energy in MWavg (val_energiavertidaturbinavel)
    - **flow_rate_turbinable_spill** *number* — Turbinable spill flow rate (m3/s) (val_vazaovertidaturbinavel)
    """
    return self.fetch_dataframe(table_name="ons_spilled_turbinable_energy", **kwargs)


def ons_stored_energy_basin(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_stored_energy_basin** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **basin_name** *string* — Name of the basin (nomecurto)
    - **reference_date** *string (date)* — Reference date of the stored energy measurement (ear_data)
    - **max_stored_energy** *number* — Maximum stored energy in MW-Month (ear_max_bacia)
    - **verified_stored_energy_mwmonth** *number* — Verified stored energy in MW-Month (ear_verif_bacia_mwmes)
    - **verified_stored_energy_percentage** *number* — Verified stored energy as percentage (ear_verif_bacia_percentual)
    """
    return self.fetch_dataframe(table_name="ons_stored_energy_basin", **kwargs)


def ons_stored_energy_equivalent_reservoir(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_stored_energy_equivalent_reservoir** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **ree_name** *string* — Name of the REE (Equivalent Energy Reservoir) (nom_ree)
    - **reference_date** *string (date)* — Reference date of the stored energy measurement (ear_data)
    - **max_stored_energy** *number* — Maximum stored energy in MW-Month (ear_max_ree)
    - **verified_stored_energy_mwmonth** *number* — Verified stored energy in MW-Month (ear_verif_ree_mwmes)
    - **verified_stored_energy_percentage** *number* — Verified stored energy as percentage (ear_verif_ree_percentual)
    """
    return self.fetch_dataframe(table_name="ons_stored_energy_equivalent_reservoir", **kwargs)


def ons_stored_energy_reservoir(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_stored_energy_reservoir** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reservoir_name** *string* — Name of the reservoir (nom_reservatorio)
    - **planning_code** *number* — Planning code of the reservoir (cod_resplanejamento)
    - **reservoir_type** *string* — Type of reservoir (tip_reservatorio)
    - **basin_name** *string* — Name of the basin (nom_bacia)
    - **electrical_region** *string* — Electrical region (nom_ree)
    - **subsystem_id** *string* — Subsystem ID (id_subsistema)
    - **subsystem_name** *string* — Subsystem name (nom_subsistema)
    - **downstream_subsystem_id** *string* — Downstream subsystem ID (id_subsistema_jusante)
    - **downstream_subsystem_name** *string* — Downstream subsystem name (nom_subsistema_jusante)
    - **reference_date** *string (date)* — Reference date of the stored energy measurement (ear_data)
    - **ear_reservoir_own_subsystem_mwmonth** *number* — Stored energy of reservoir in its own subsystem in MW-Month (ear_reservatorio_subsistema_proprio_mwmes)
    - **ear_reservoir_downstream_subsystem_mwmonth** *number* — Stored energy of reservoir in downstream subsystem in MW-Month (ear_reservatorio_subsistema_jusante_mwmes)
    - **earmax_reservoir_own_subsystem_mwmonth** *number* — Maximum stored energy of reservoir in its own subsystem in MW-Month (earmax_reservatorio_subsistema_proprio_mwmes)
    - **earmax_reservoir_downstream_subsystem_mwmonth** *number* — Maximum stored energy of reservoir in downstream subsystem in MW-Month (earmax_reservatorio_subsistema_jusante_mwmes)
    - **ear_reservoir_percentage** *number* — Stored energy as percentage (ear_reservatorio_percentual)
    - **ear_total_mwmonth** *number* — Total stored energy in MW-Month (ear_total_mwmes)
    - **ear_max_total_mwmonth** *number* — Maximum total stored energy in MW-Month (ear_maxima_total_mwmes)
    - **contrib_ear_basin** *number* — Contribution to stored energy of basin (val_contribearbacia)
    - **contrib_ear_max_basin** *number* — Contribution to maximum stored energy of basin (val_contribearmaxbacia)
    - **contrib_ear_subsystem** *number* — Contribution to stored energy of subsystem (val_contribearsubsistema)
    - **contrib_ear_max_subsystem** *number* — Contribution to maximum stored energy of subsystem (val_contribearmaxsubsistema)
    - **contrib_ear_downstream_subsystem** *number* — Contribution to stored energy of downstream subsystem (val_contribearsubsistemajusante)
    - **contrib_ear_max_downstream_subsystem** *number* — Contribution to maximum stored energy of downstream subsystem (val_contribearmaxsubsistemajusante)
    - **contrib_ear_sin** *number* — Contribution to stored energy of SIN (val_contribearsin)
    - **contrib_ear_max_sin** *number* — Contribution to maximum stored energy of SIN (val_contribearmaxsin)
    """
    return self.fetch_dataframe(table_name="ons_stored_energy_reservoir", **kwargs)


def ons_stored_energy_subsystem(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_stored_energy_subsystem** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **max_stored_energy** *number* — Maximum stored energy in the subsystem in MW-Month
    - **verified_stored_energy_mwmonth** *number* — Verified stored energy on reference_date in the subsystem in MW-Month
    - **verified_stored_energy_percentage** *number* — Verified stored energy on reference_date in the subsystem in percentage
    - **reference_date** *string (date)* — Timestamp of the stored energy
    - **subsystem** *enum* — Subsystem of the stored energy ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    """
    return self.fetch_dataframe(table_name="ons_stored_energy_subsystem", **kwargs)


def ons_thermal_generation_dispatch_reason(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_thermal_generation_dispatch_reason** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Timestamp of the thermal generation dispatch reason (din_instante)
    - **load_level** *enum* — Hourly load level (Light, Medium, Heavy) (nom_tipopatamar) ['LEVE', 'MEDIA', 'PESADA']
    - **subsystem** *enum* — Subsystem name (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **generator_name** *string* — Plant name (nom_usina)
    - **planning_generator_code** *string* — Plant code in planning and operation programming models (cod_usinaplanejamento)
    - **ceg** *string* — Unique Generation Enterprise Code (CEG) established by ANEEL (ceg)
    - **scheduled_generation_total** *number* — Total scheduled generation in MWavg (val_proggeracao)
    - **scheduled_generation_by_merit** *number* — Scheduled generation by merit order in MWavg (val_progordemmerito)
    - **scheduled_generation_by_merit_reference** *number* — Reference for merit order dispatch in MWavg (val_progordemdemeritoref)
    - **scheduled_generation_by_merit_no_inflexible** *number* — Scheduled generation by merit order, excluding embedded inflexibility, in MWavg (val_progordemdemeritoacimadainflex)
    - **scheduled_generation_inflexible** *number* — Scheduled inflexible generation in MWavg (val_proginflexibilidade)
    - **scheduled_generation_by_merit_inflexible** *number* — Scheduled generation ranked by merit order with embedded inflexibility, in MWavg (val_proginflexembutmerito)
    - **scheduled_generation_by_merit_pure_inflexible** *number* — Scheduled generation by merit order, excluding embedded inflexibility (pure inflexibility), in MWavg (val_proginflexpura)
    - **scheduled_generation_electrical_reason** *number* — Scheduled generation for electrical reason or SIN necessity in MWavg (val_prograzaoeletrica)
    - **scheduled_generation_energy_guarantee** *number* — Scheduled generation for energy security guarantee in MWavg (val_proggarantiaenergetica)
    - **scheduled_generation_out_of_merit** *number* — Out of merit order scheduled generation (GFOM) in MWavg (val_proggfom)
    - **scheduled_generation_loss_replacement** *number* — Scheduled generation for loss replacement in MWavg (val_progreposicaoperdas)
    - **scheduled_generation_export** *number* — Scheduled generation for export in MWavg (val_progexportacao)
    - **scheduled_generation_power_reserve** *number* — Scheduled generation for power reserve in MWavg (val_progreservapotencia)
    - **scheduled_generation_out_of_merit_substitute** *number* — Out of merit order scheduled generation to substitute another plant with lower operation cost, due to a fuel constraint (GSUB) in MWavg (val_proggsub)
    - **scheduled_generation_unit_commitment** *number* — Scheduled generation for unit commitment in MWavg (val_progunitcommitment)
    - **scheduled_generation_curtailed** *number* — Curtailed scheduled generation in MWavg (val_progconstrainedoff)
    - **scheduled_generation_inflexible_dessem** *number* — Scheduled inflexibility from DESSEM in MWavg (val_proginflexibilidadedessem)
    - **verified_generation_total** *number* — Total verified generation in MWavg (val_verifgeracao)
    - **verified_generation_by_merit** *number* — Verified generation by merit order in MWavg (val_verifordemmerito)
    - **verified_generation_by_merit_no_inflexible** *number* — Verified generation by merit order, excluding embedded inflexibility, in MWavg (val_verifordemdemeritoacimadainflex)
    - **verified_generation_inflexible** *number* — Verified inflexible generation in MWavg (val_verifinflexibilidade)
    - **verified_generation_by_merit_inflexible** *number* — Verified generation with inflexibility embedded in merit order in MWavg (val_verifinflexembutmerito)
    - **verified_generation_by_merit_pure_inflexible** *number* — Verified generation with inflexibility not embedded in merit order (pure inflexibility) in MWavg (val_verifinflexpura)
    - **verified_generation_electrical_reason** *number* — Verified generation for electrical reason or SIN necessity in MWavg (val_verifrazaoeletrica)
    - **verified_generation_energy_guarantee** *number* — Verified generation for energy security guarantee in MWavg (val_verifgarantiaenergetica)
    - **verified_generation_out_of_merit** *number* — Verified generation out of merit in MWavg (val_verifgfom)
    - **verified_generation_loss_replacement** *number* — Verified generation for loss replacement in MWavg (val_verifreposicaoperdas)
    - **verified_generation_export** *number* — Verified generation for export in MWavg (val_verifexportacao)
    - **export_code_semi_hourly** *enum* — Indicates the type of energy export in semi-hourly load (val_fdexp) [0.0, 0.5, 1.0]
    - **verified_generation_power_reserve** *number* — Verified generation for power reserve in MWavg (val_verifreservapotencia)
    - **reserve_generation_compliance_code** *enum* — Classification of satisfactory compliance with dispatch for operational reserve replenishment (val_atendsatisfatoriorpo) [0.0, 1.0, 2.0]
    - **verified_generation_out_of_merit_substitute** *number* — Verified generation GSUB in MWavg (val_verifgsub)
    - **verified_generation_unit_commitment** *number* — Verified generation for unit commitment in MWavg (val_verifunitcommitment)
    - **verified_generation_curtailed** *number* — Curtailed verified generation in MWavg (val_verifconstrainedoff)
    - **electric_restriction** *enum* — Type of electric restriction (tip_restricaoeletrica). [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return self.fetch_dataframe(table_name="ons_thermal_generation_dispatch_reason", **kwargs)


def ons_thermal_operation_cost(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_thermal_operation_cost** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_week_start** *string (date-time)* — Start date of the reference week for the thermal operation cost (dat_iniciosemana).
    - **reference_week_end** *string (date-time)* — End date of the reference week for the thermal operation cost (dat_fimsemana).
    - **reference_month** *integer* — Monthly Operation Planning (PMO) reference month for the thermal operation cost (mes_referencia).
    - **revision_number** *integer* — Monthly Operation Planning (PMO) revision number of the thermal operation cost data (num_revisao).
    - **subsystem** *enum* — Subsystem (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **generator_name** *string* — Name of the generator (nom_usina)
    - **generator_code** *string* — Planning generator code (cod_usinaplanejamento)
    - **cost** *number* — Variable cost of operation R$/MWh (val_cvu).
    """
    return self.fetch_dataframe(table_name="ons_thermal_operation_cost", **kwargs)


def ons_wind_and_solar_capacity_factor_hourly(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_wind_and_solar_capacity_factor_hourly** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **subsystem** *enum* — Subsystem from (nom_subsistema) ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **state_code** *enum* — State code (id_estado) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **reference_date** *string (date-time)* — Reference date and time of the capacity factor measurement (din_instante)
    - **connection_point** *string* — Connection point (nom_pontoconexao)
    - **connection_point_code** *string* — Connection point code (cod_pontoconexao)
    - **location_name** *string* — Location name (nom_localizacao)
    - **generator_latitude** *number* — Latitude of the location (val_latitudesecoletora)
    - **generator_longitude** *number* — Longitude of the location (val_longitudesecoletora)
    - **connection_point_latitude** *number* — Latitude of the connection point (val_latitudepontoconexao)
    - **connection_point_longitude** *number* — Longitude of the connection point (val_longitudepontoconexao)
    - **operation_mode** *enum* — Operation mode of the plant (nom_modalidadeoperacao) ['TIPO I', 'TIPO II-A', 'TIPO II-B', 'TIPO II-C', 'TIPO III', 'MMGD']
    - **plant_type** *enum* — Type of the plant (nom_tipousina) ['HIDROELÉTRICA', 'TÉRMICA', 'EOLIELÉTRICA', 'FOTOVOLTAICA', 'NUCLEAR', 'BOMBEAMENTO']
    - **plant_set** *string* — Plant set (nom_usina_conjunto)
    - **ons_id** *string* — ONS ID of the plant set (id_ons)
    - **ceg** *string* — ONS CEG of the plant set (ceg)
    - **generation_scheduled** *number* — Scheduled generation in MWavg (val_geracaoprogramada)
    - **generation_verified** *number* — Verified generation in MWavg (val_geracaoverificada)
    - **installed_capacity** *number* — Installed capacity in MWavg (val_capacidadeinstalada)
    - **capacity_factor** *number* — Capacity factor (val_fatorcapacidade)
    """
    return self.fetch_dataframe(table_name="ons_wind_and_solar_capacity_factor_hourly", **kwargs)


def ons_wind_and_solar_predicted_versus_scheduled(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_wind_and_solar_predicted_versus_scheduled** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Reference date for the data (dat_programacao).
    - **level** *integer* — Number of level (num_patamar)
    - **plant_code** *string* — Code of the plant (cod_usinapdp)
    - **plant_name** *string* — Name of the plant (nom_usinapdp)
    - **generation_predicted** *number* — Forecasted generation (val_previsao)
    - **generation_scheduled** *number* — Scheduled generation (val_programado)
    """
    return self.fetch_dataframe(table_name="ons_wind_and_solar_predicted_versus_scheduled", **kwargs)


def ons_wind_curtailment(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_wind_curtailment** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Timestamp of the stored energy
    - **subsystem** *enum* — Subsystem ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **state_code** *enum* — State ID of the generator set (id_estado - Installed Capacity) ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **generator_name** *string* — Name of the generator (nom_usina)
    - **ons_id** *string* — ONS ID of the generator set (id_ons)
    - **ceg** *string* — ONS CEG ID of the generator set (ceg)
    - **generation** *number* — Generated energy in MWh (val_geracao) / 2
    - **limited_generation** *number* — Limited generation in MWh (val_geracaolimitada) / 2
    - **generation_availability** *number* — Generation availability in MWh (val_disponibilidade) / 2
    - **generation_reference** *number* — Generation reference in MWh (val_geracaoreferencia) / 2
    - **generation_final_reference** *number* — Final generation reference in MWh (val_geracaoreferenciafinal) / 2
    - **reason_code** *enum* — Curtailment reason code (cod_razaorestricao) ['REL', 'CNF', 'ENE', 'PAR']
    - **source_code** *enum* — Curtailment source code (cod_origemrestricao) ['LOC', 'SIS']
    - **description** *string* — Description of the curtailment reason (dsc_restricao)
    - **physical_curtailment** *number* — Physical curtailment in MWh
    - **unconstrained_generation** *number* — Unconstrained generation in MWh (generation + physical_curtailment)
    """
    return self.fetch_dataframe(table_name="ons_wind_curtailment", **kwargs)


def ons_wind_curtailment_detailed(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **ons_wind_curtailment_detailed** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **reference_date** *string (date-time)* — Reference date for the data (din_instante).
    - **subsystem** *enum* — Subsystem identifier. Represents the electrical subsystem within the National Interconnected System (SIN)(sub_sistema). ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
    - **state_code** *enum* — State code. Abbreviation of the state where the plant is located (id_estado). ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    - **operation_mode** *enum* — Plant operation mode. Indicates the operational modality of the wind plant (nom_modalidadeoperacao). ['TIPO I', 'TIPO II-A', 'TIPO II-B', 'TIPO II-C', 'TIPO III', 'MMGD']
    - **plant_set** *string* — Plant set name. Name of the plant set, applicable only for plants operating under Type II-C modality (nom_conjuntousina).
    - **generator_name** *string* — Generator name. Official name of the wind power plant as registered in ONS systems (nom_usina).
    - **ons_id** *string* — ONS plant identifier (id_ons).
    - **ceg** *string* — CEG (ceg).
    - **verified_wind** *number* — Verified wind speed. Measured wind data in m/s at the plant's location (val_ventoverificado).
    - **invalid_wind_data** *boolean* — Invalid wind data flag. Indicates whether the wind measurement is invalid due to a monitoring failure lasting more than six minutes within the corresponding half-hour period (flg_dadoventoinvalido).
    - **estimated_generation** *number* — Estimated average power generation in MWavg , calculated from the verified wind data and the wind power curve, or based on historical verified generation if the curve is unavailable (val_geracaoestimada).
    - **verified_generation** *number* — Measured average power generation of the plant in MWavg (val_geracaoverificada).
    """
    return self.fetch_dataframe(table_name="ons_wind_curtailment_detailed", **kwargs)


def r_e_d_e_m_e_t_meteorological_report(self, **kwargs) -> "pd.DataFrame":
    """Fetch data from the **r_e_d_e_m_e_t_meteorological_report** table.

    Accepts the same keyword arguments as ``fetch_dataframe``
    (e.g. data_columns, filters, start_reference_date, …).

    Available columns:
    - **station** *string* — ICAO airport code
    - **station_name** *string* — Airport name
    - **reference_date** *string (date-time)* — Observation timestamp
    - **wind_direction** *integer* — Wind direction in degrees
    - **wind_speed** *number* — Wind speed in knots
    - **wind_gust** *number* — Wind gust speed in knots
    - **raw_message** *string* — Raw METAR message
    """
    return self.fetch_dataframe(table_name="r_e_d_e_m_e_t_meteorological_report", **kwargs)


def register_aliases():
    """Attach all table alias methods to the Client class."""
    from psr.lakehouse.client import Client

    Client.aneel_distributed_generation_projects = aneel_distributed_generation_projects
    Client.ccee_spot_price = ccee_spot_price
    Client.ccee_spot_price_average_monthly = ccee_spot_price_average_monthly
    Client.ccee_spot_price_historical_weekly = ccee_spot_price_historical_weekly
    Client.c_e_g = c_e_g
    Client.c_e_g_data = c_e_g_data
    Client.e_p_e_energy_consumption_monthly = e_p_e_energy_consumption_monthly
    Client.generator_generator_unit = generator_generator_unit
    Client.generator_unit = generator_unit
    Client.ons_commercial_generation_international_export = ons_commercial_generation_international_export
    Client.ons_controlled_power_flow_program_daily = ons_controlled_power_flow_program_daily
    Client.ons_energy_balance_subsystem = ons_energy_balance_subsystem
    Client.ons_energy_import_commercial_block = ons_energy_import_commercial_block
    Client.ons_energy_import_price_bids = ons_energy_import_price_bids
    Client.ons_energy_load_daily = ons_energy_load_daily
    Client.ons_energy_load_monthly = ons_energy_load_monthly
    Client.ons_energy_load_verified = ons_energy_load_verified
    Client.ons_exchange_international = ons_exchange_international
    Client.ons_exchange_modality = ons_exchange_modality
    Client.ons_exchange_subsystem = ons_exchange_subsystem
    Client.ons_generator_data = ons_generator_data
    Client.ons_generator_unit_data = ons_generator_unit_data
    Client.ons_hydrological_reservoir_data_daily = ons_hydrological_reservoir_data_daily
    Client.ons_hydrological_reservoir_data_hourly = ons_hydrological_reservoir_data_hourly
    Client.ons_inflow_energy_basin = ons_inflow_energy_basin
    Client.ons_inflow_energy_equivalent_reservoir = ons_inflow_energy_equivalent_reservoir
    Client.ons_inflow_energy_reservoir = ons_inflow_energy_reservoir
    Client.ons_inflow_energy_subsystem = ons_inflow_energy_subsystem
    Client.ons_load_curve = ons_load_curve
    Client.ons_load_marginal_cost_semi_hourly = ons_load_marginal_cost_semi_hourly
    Client.ons_load_marginal_cost_weekly = ons_load_marginal_cost_weekly
    Client.ons_power_plant_availability = ons_power_plant_availability
    Client.ons_power_plant_hourly_generation = ons_power_plant_hourly_generation
    Client.ons_solar_curtailment = ons_solar_curtailment
    Client.ons_solar_curtailment_detailed = ons_solar_curtailment_detailed
    Client.ons_spilled_turbinable_energy = ons_spilled_turbinable_energy
    Client.ons_stored_energy_basin = ons_stored_energy_basin
    Client.ons_stored_energy_equivalent_reservoir = ons_stored_energy_equivalent_reservoir
    Client.ons_stored_energy_reservoir = ons_stored_energy_reservoir
    Client.ons_stored_energy_subsystem = ons_stored_energy_subsystem
    Client.ons_thermal_generation_dispatch_reason = ons_thermal_generation_dispatch_reason
    Client.ons_thermal_operation_cost = ons_thermal_operation_cost
    Client.ons_wind_and_solar_capacity_factor_hourly = ons_wind_and_solar_capacity_factor_hourly
    Client.ons_wind_and_solar_predicted_versus_scheduled = ons_wind_and_solar_predicted_versus_scheduled
    Client.ons_wind_curtailment = ons_wind_curtailment
    Client.ons_wind_curtailment_detailed = ons_wind_curtailment_detailed
    Client.r_e_d_e_m_e_t_meteorological_report = r_e_d_e_m_e_t_meteorological_report
