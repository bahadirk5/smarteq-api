import pandas as pd
from datetime import datetime
from django.db import transaction
from apps.inventory.repositories.excel_import_repository import ExcelImportRepository
from apps.inventory.repositories.item_repository import ItemRepository
from apps.inventory.repositories.category_repository import CategoryRepository
from apps.inventory.repositories.purchase_history_repository import PurchaseHistoryRepository
from apps.inventory.repositories.bill_of_materials_repository import BillOfMaterialsRepository
from apps.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from apps.inventory.models import Category
from apps.inventory.models.excel_import import ExcelImport
from apps.projects.repositories.project_inventory_repository import ProjectInventoryRepository
from apps.projects.repositories.project_repository import ProjectRepository
from apps.projects.services.project_inventory_service import ProjectInventoryService
from apps.common.utils.logger import logger
import traceback
import uuid


class ExcelImportService:
    """
    Service class for managing Excel imports for inventory
    """
    @staticmethod
    def create_import(import_type, file, notes=None, processed_by=None, project_id=None):
        """
        Create a new Excel import record
        
        Args:
            import_type (str): The type of import ('RAW_MATERIALS', 'PRODUCTS', etc.)
            file (File): Uploaded Excel file
            notes (str, optional): Additional notes
            processed_by (User, optional): User processing the import
            project_id (str, optional): ID of the project to associate items with
        """
        if import_type not in ['RAW_MATERIALS', 'PRODUCTS', 'BOM', 'ELECTRONIC_COMPONENTS']:
            return None, "Invalid import type"
            
        # Project ID validation (if provided)
        if project_id:
            project_repository = ProjectRepository()
            try:
                project = project_repository.get(id=project_id)
                if not project.is_active:
                    return None, "Selected project is not active"
            except Exception as e:
                logger.error(f"Project validation error in create_import: {str(e)}")
                return None, "Selected project does not exist"
        
        # Prepare full notes with project_id if provided
        full_notes = notes if notes else ""
        if project_id:
            if full_notes:
                full_notes += " | "
            full_notes += f"PROJECT_ID:{project_id}"
            
        # Repository'nin beklediği parametrelere göre oluştur
        excel_import = ExcelImportRepository.create(
            import_type=import_type,
            file=file,
            notes=full_notes,
            processed_by=processed_by
        )
        
        if not excel_import:
            return None, "Failed to create import record"
            
        return excel_import, None
    
    @staticmethod
    def get_imports(order_by='-created_at', **filters):
        """
        Get all Excel imports with optional filters
        """
        return ExcelImportRepository.get_all(order_by=order_by, **filters), None
    
    @staticmethod
    def get_import_by_id(import_id):
        """
        Get Excel import by id
        """
        excel_import = ExcelImportRepository.get_by_id(import_id)
        if not excel_import:
            return None, "Import record not found"
            
        return excel_import, None
    
    @staticmethod
    def process_raw_materials_import(import_id):
        """
        Process raw materials Excel import
        Expected columns:
        - sku: Item SKU (required)
        - name: Item name (required)
        - description: Item description
        - category: Category name
        - unit_of_measure: Unit of measure (required)
        - quantity: Initial quantity
        - purchase_price: Purchase price per unit
        - purchase_date: Date of purchase (YYYY-MM-DD)
        - supplier: Supplier name
        - invoice_reference: Invoice reference
        """
        excel_import = ExcelImportRepository.get_by_id(import_id)
        if not excel_import:
            return False, "Import record not found"
            
        if excel_import.import_type != 'RAW_MATERIALS':
            return False, "Import type is not RAW_MATERIALS"
            
        if excel_import.status != 'PENDING':
            return False, "Import already processed"
        
        try:
            # Update status to processing
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='PROCESSING'
            )
            
            # Read Excel file
            df = pd.read_excel(excel_import.file.path)
            
            required_cols = ['sku', 'name', 'unit_of_measure']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in Excel file")
            
            processed_count = 0
            failed_count = 0
            error_details = []
            
            # Process each row
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        sku = str(row['sku']).strip()
                        name = str(row['name']).strip()
                        unit_of_measure = str(row['unit_of_measure']).strip()
                        
                        # Optional fields
                        description = str(row.get('description', '')).strip() if pd.notna(row.get('description', '')) else None
                        category_name = str(row.get('category', '')).strip() if pd.notna(row.get('category', '')) else None
                        quantity = int(row.get('quantity', 0)) if pd.notna(row.get('quantity', 0)) else 0
                        purchase_price = float(row.get('purchase_price', 0)) if pd.notna(row.get('purchase_price', 0)) else 0
                        purchase_date_str = str(row.get('purchase_date', '')).strip() if pd.notna(row.get('purchase_date', '')) else None
                        supplier = str(row.get('supplier', '')).strip() if pd.notna(row.get('supplier', '')) else None
                        invoice_reference = str(row.get('invoice_reference', '')).strip() if pd.notna(row.get('invoice_reference', '')) else None
                        
                        # Get or create category
                        category = None
                        if category_name:
                            category = CategoryRepository.get_by_name(category_name)
                            if not category:
                                category = CategoryRepository.create(name=category_name)
                        
                        # Check if item already exists
                        item = ItemRepository.get_by_sku(sku)
                        
                        if item:
                            # Update existing item
                            item = ItemRepository.update(
                                item_id=item.id,
                                name=name,
                                description=description,
                                category=category,
                                unit_of_measure=unit_of_measure,
                                purchase_price=purchase_price
                            )
                        else:
                            # Create new item
                            item = ItemRepository.create(
                                name=name,
                                sku=sku,
                                description=description,
                                item_type='RAW',
                                category=category,
                                unit_of_measure=unit_of_measure,
                                quantity=quantity,
                                purchase_price=purchase_price,
                                sales_list_status='NOT_LISTED'
                            )
                        
                        # Create purchase history if purchase_date and purchase_price are provided
                        if purchase_date_str and purchase_price > 0:
                            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                            PurchaseHistoryRepository.create(
                                item=item,
                                purchase_date=purchase_date,
                                quantity=quantity,
                                unit_price=purchase_price,
                                supplier=supplier,
                                invoice_reference=invoice_reference
                            )
                        
                        processed_count += 1
                    except Exception as e:
                        failed_count += 1
                        error_details.append(f"Row {index+2}: {str(e)}")
            
            # Update import status
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='COMPLETED' if failed_count == 0 else 'FAILED',
                processed_count=processed_count,
                failed_count=failed_count,
                error_details='\n'.join(error_details) if error_details else None
            )
            
            return True, None
        except Exception as e:
            # Update import status
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='FAILED',
                error_details=str(e)
            )
            
            return False, str(e)
    
    @staticmethod
    def process_bom_import(import_id):
        """
        Process Bill of Materials Excel import
        Expected columns:
        - output_sku: SKU of output item (required)
        - input_sku: SKU of input item (required)
        - quantity_required: Quantity required (required)
        - unit_of_measure: Unit of measure (required)
        - sequence: Assembly sequence
        - is_optional: Whether component is optional (Y/N)
        - is_default: Whether component is default (Y/N)
        - alternative_group: Group ID for alternative components
        """
        excel_import = ExcelImportRepository.get_by_id(import_id)
        if not excel_import:
            return False, "Import record not found"
            
        if excel_import.import_type != 'BOM':
            return False, "Import type is not BOM"
            
        if excel_import.status != 'PENDING':
            return False, "Import already processed"
        
        try:
            # Update status to processing
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='PROCESSING'
            )
            
            # Read Excel file
            df = pd.read_excel(excel_import.file.path)
            
            required_cols = ['output_sku', 'input_sku', 'quantity_required', 'unit_of_measure']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in Excel file")
            
            processed_count = 0
            failed_count = 0
            error_details = []
            
            # Process each row
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        output_sku = str(row['output_sku']).strip()
                        input_sku = str(row['input_sku']).strip()
                        quantity_required = float(row['quantity_required'])
                        unit_of_measure = str(row['unit_of_measure']).strip()
                        
                        # Optional fields
                        sequence = int(row.get('sequence', 10)) if pd.notna(row.get('sequence', 10)) else 10
                        is_optional = True if pd.notna(row.get('is_optional', '')) and str(row.get('is_optional', '')).upper() == 'Y' else False
                        is_default = False if pd.notna(row.get('is_default', '')) and str(row.get('is_default', '')).upper() == 'N' else True
                        alternative_group = str(row.get('alternative_group', '')).strip() if pd.notna(row.get('alternative_group', '')) else None
                        
                        # Get output and input items
                        output_item = ItemRepository.get_by_sku(output_sku)
                        input_item = ItemRepository.get_by_sku(input_sku)
                        
                        if not output_item:
                            raise ValueError(f"Output item with SKU '{output_sku}' not found")
                            
                        if not input_item:
                            raise ValueError(f"Input item with SKU '{input_sku}' not found")
                        
                        # Check if BOM entry already exists
                        bom = BillOfMaterialsRepository.get_by_items(output_item.id, input_item.id)
                        
                        if bom:
                            # Update existing BOM entry
                            bom = BillOfMaterialsRepository.update(
                                bom_id=bom.id,
                                quantity_required=quantity_required,
                                unit_of_measure=unit_of_measure,
                                sequence=sequence,
                                is_optional=is_optional,
                                is_default=is_default,
                                alternative_group=alternative_group
                            )
                        else:
                            # Create new BOM entry
                            bom = BillOfMaterialsRepository.create(
                                output_item=output_item,
                                input_item=input_item,
                                quantity_required=quantity_required,
                                unit_of_measure=unit_of_measure,
                                sequence=sequence,
                                is_optional=is_optional,
                                is_default=is_default,
                                alternative_group=alternative_group
                            )
                        
                        processed_count += 1
                    except Exception as e:
                        failed_count += 1
                        error_details.append(f"Row {index+2}: {str(e)}")
            
            # Update import status
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='COMPLETED' if failed_count == 0 else 'FAILED',
                processed_count=processed_count,
                failed_count=failed_count,
                error_details='\n'.join(error_details) if error_details else None
            )
            
            return True, None
        except Exception as e:
            # Update import status
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='FAILED',
                error_details=str(e)
            )
            
            return False, str(e)

    @staticmethod
    def process_products_import(import_id):
        """
        Process products Excel import
        Expected columns:
        - Name: Product name (required) - Also used to generate SKU if not present
        - Value: Product value (if SKU is not present, used to generate SKU)
        - Qty: Initial quantity
        - SKU: Stock keeping unit (optional)
        - Category: Category name
        - Unit: Unit of measure (required)
        - Price: Selling price
        - Cost: Production cost
        - Description: Product description
        """
        excel_import = ExcelImportRepository.get_by_id(import_id)
        if not excel_import:
            return False, "Import record not found"
            
        if excel_import.import_type != 'PRODUCTS':
            return False, "Import type is not PRODUCTS"
            
        if excel_import.status != 'PENDING':
            return False, "Import already processed"
        
        try:
            # Get project_id from notes if available
            project_id = ExcelImportService._extract_project_id_from_import(excel_import)
            
            # Validate project exists
            project, error_message = ExcelImportService._validate_project(project_id)
            if error_message:
                return False, error_message
            
            # Update status to processing
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='PROCESSING'
            )
            
            # Read Excel file
            df = pd.read_excel(excel_import.file.path)
            
            # Check required columns based on structure
            required_cols = ['Name', 'Unit']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in Excel file")
            
            processed_count = 0
            failed_count = 0
            error_details = []

            # Repository instances
            item_repo = ItemRepository()
            inventory_transaction_repo = InventoryTransactionRepository()
            
            # Process each row
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        name = str(row['Name']).strip()
                        unit = str(row['Unit']).strip()
                        
                        # Determine SKU - either use explicit SKU if present or generate from Name/Value
                        if 'SKU' in df.columns and pd.notna(row.get('SKU')):
                            sku = str(row['SKU']).strip()
                        else:
                            # Generate SKU from name and value
                            prefix = 'FP-'  # Final Product prefix
                            base = name[:3].upper()
                            sku = f"{prefix}{base}{(index+1):03d}"
                            
                        item_data = {
                            'sku': sku,
                            'name': name,
                            'description': str(row.get('Description', '')).strip() if pd.notna(row.get('Description', '')) else None,
                            'item_type': 'FINAL',  # Ürünler daima final product
                            'unit_of_measure': unit,
                            'quantity': int(row.get('Qty', 0)) if pd.notna(row.get('Qty', 0)) else 0,
                            'selling_price': float(row.get('Price', 0)) if pd.notna(row.get('Price', 0)) else 0,
                            'purchase_price': float(row.get('Cost', 0)) if pd.notna(row.get('Cost', 0)) else 0,
                            'minimum_stock_level': 1
                        }
                        
                        if 'Category' in df.columns and pd.notna(row.get('Category')):
                            category_path = str(row['Category']).strip()
                            category = ExcelImportService.get_or_create_category_hierarchy(category_path)
                            if category:
                                item_data['category_id'] = category.id
                        
                        # Check if item already exists
                        existing_item = None
                        try:
                            existing_item = ItemRepository.get_by_sku(sku)
                        except Exception:
                            pass
                            
                        if existing_item:
                            # Update existing item
                            item = ItemRepository.update(existing_item.id, item_data)
                        else:
                            # Create new item
                            item = ItemRepository.create(**item_data)
                            
                        # Add item to project inventory if project_id is available
                        if project_id and item:
                            success, error_message = ExcelImportService._add_item_to_project_inventory(item.id, project_id, item_data['quantity'], row_index=index)
                            if not success:
                                error_details.append(error_message)
                        
                        # Create initial inventory transaction if quantity > 0
                        if item_data['quantity'] > 0:
                            try:
                                InventoryTransactionRepository.create_transaction(**{
                                    'item_id': item.id,
                                    'transaction_type': 'INITIAL',
                                    'quantity': item_data['quantity'],
                                    'reference_model': 'ExcelImport',
                                    'reference_id': excel_import.id,
                                    'notes': f"Initial stock from Excel import. Import ID: {import_id}"
                                })
                            except Exception as tx_e:
                                # Log transaction error but continue with next item
                                error_details.append(f"Row {index+2} (Initial Transaction): {str(tx_e)}")
                        
                        processed_count += 1
                    except Exception as e:
                        failed_count += 1
                        error_details.append(f"Row {index+2}: {str(e)}")
            
            # Update import status
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='COMPLETED' if failed_count == 0 else 'FAILED',
                processed_count=processed_count,
                failed_count=failed_count,
                error_details='\n'.join(error_details) if error_details else None
            )
            
            return True, None
        except Exception as e:
            # Update import status
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='FAILED',
                error_details=str(e)
            )
            
            return False, str(e)

    @staticmethod
    def process_electronic_components_import(import_id):
        """
        Process electronic components Excel import
        Expected columns (based on PCB components Excel format):
        - Reference: Component reference designators (e.g., R6,R7,R8) 
        - Qty: Quantity of components
        - Value: Component value (e.g., 0R, 10pF) - Used as SKU and name
        - MPN: Manufacturer Part Number
        - Footprint: Component footprint (e.g., Resistor_SMD:R_0402_1005Metric)
        """
        excel_import = ExcelImportRepository.get_by_id(import_id)
        if not excel_import:
            return False, "Import record not found"
            
        if excel_import.import_type != 'ELECTRONIC_COMPONENTS':
            return False, "Import type is not ELECTRONIC_COMPONENTS"
            
        if excel_import.status != 'PENDING':
            return False, "Import already processed"
        
        try:
            # Get project_id from notes if available
            project_id = ExcelImportService._extract_project_id_from_import(excel_import)
            
            # Proje ID eksikse hata ver
            if not project_id:
                return False, "Excel importu için proje seçimi zorunludur. Lütfen bir proje seçin."
            
            # Validate project exists
            project, error_message = ExcelImportService._validate_project(project_id)
            if error_message:
                return False, error_message
            
            # Update status to processing
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='PROCESSING'
            )
            
            # Read Excel file
            df = pd.read_excel(excel_import.file.path)
            
            # Check required columns
            required_cols = ['Reference', 'Qty', 'Value', 'MPN', 'Footprint']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in Excel file")
            
            processed_count = 0
            failed_count = 0
            error_details = []
            
            # Repository instances
            item_repo = ItemRepository()
            inventory_transaction_repo = InventoryTransactionRepository()
            
            # Ensure electronic components category exists
            electronic_category = ExcelImportService.get_or_create_category_hierarchy('Elektronik Komponentler')
            
            # Process each row
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        reference = str(row['Reference']).strip()
                        quantity = int(row['Qty'])
                        value = str(row['Value']).strip()
                        mpn = str(row['MPN']).strip()
                        footprint = str(row['Footprint']).strip()
                        
                        # Use Value as SKU and name - normalized for database use
                        value_normalized = value.replace(' ', '-').replace('/', '-').replace('.', '_')[:20]
                        sku = f"COMP-{value_normalized}"
                        
                        # Build description with MPN and footprint
                        description = f"MPN: {mpn}\nFootprint: {footprint}"
                        
                        # Check if item already exists - handle errors gracefully
                        try:
                            # Try to get the item - if not found, will raise exception
                            item = item_repo.get_item_by_sku(sku)
                            
                            # Update existing item
                            item_repo.update_item(
                                item_id=item.id,
                                item_data={
                                    'name': value,  # Use component value as name
                                    'description': description,
                                    'reference': reference,
                                    'unit_of_measure': 'pcs',
                                    'category': electronic_category
                                }
                            )
                            
                            # Update quantity through inventory transaction
                            try:
                                previous_qty = item.quantity
                                quantity_change = quantity - previous_qty
                                
                                if quantity_change != 0:
                                    item_repo.update_item_quantity(
                                        item_id=item.id,
                                        quantity=quantity
                                    )
                                    
                                    # Record transaction for the quantity change
                                    inventory_transaction_repo.create_transaction({
                                        'item': item,
                                        'transaction_type': 'ADJUSTMENT',
                                        'quantity': quantity_change,
                                        'reference_model': 'ExcelImport',
                                        'reference_id': 1,  
                                        'notes': f"Excel import adjustment for {value} ({mpn}). Import ID: {import_id}"
                                    })
                            except Exception as tx_e:
                                # Log transaction error but continue with next item
                                error_details.append(f"Row {index+2} (Transaction): {str(tx_e)}")
                        except:
                            # Create new item
                            try:
                                # Create the new item
                                item = item_repo.create_item({
                                    'sku': sku,
                                    'name': value,  # Use component value as name
                                    'description': description,
                                    'reference': reference,
                                    'item_type': 'RAW',  # Components are raw materials
                                    'category': electronic_category,
                                    'unit_of_measure': 'pcs',
                                    'quantity': quantity
                                })
                                
                                # Record transaction for the initial quantity
                                if quantity > 0:
                                    try:
                                        inventory_transaction_repo.create_transaction({
                                            'item': item,
                                            'transaction_type': 'ADJUSTMENT',
                                            'quantity': quantity,
                                            'reference_model': 'ExcelImport',
                                            'reference_id': 1,  
                                            'notes': f"Initial stock from Excel import for {value} ({mpn}). Import ID: {import_id}"
                                        })
                                    except Exception as tx_e:
                                        # Log transaction error but continue with next item
                                        error_details.append(f"Row {index+2} (Initial Transaction): {str(tx_e)}")
                            except Exception as create_e:
                                # Handle creation errors
                                raise Exception(f"Failed to create component: {str(create_e)}")
                        
                        # Add item to project inventory if project_id is available
                        if project_id:
                            success, error_message = ExcelImportService._add_item_to_project_inventory(item.id, project_id, quantity, row_index=index)
                            if not success:
                                error_details.append(error_message)
                        
                        processed_count += 1
                    except Exception as e:
                        failed_count += 1
                        error_details.append(f"Row {index+2}: {str(e)}")
            
            # Update import status
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='COMPLETED' if failed_count == 0 else 'FAILED',
                processed_count=processed_count,
                failed_count=failed_count,
                error_details='\n'.join(error_details) if error_details else None
            )
            
            return True, None
        except Exception as e:
            # Update import status
            ExcelImportRepository.update_status(
                import_id=import_id,
                status='FAILED',
                error_details=str(e)
            )
            
            return False, str(e)

    @staticmethod
    def update_import_notes_with_project_id(import_id, project_id):
        """
        Excel import kaydının notlarını günceller ve proje ID'yi ekler.
        SmartEQ mimarisine uygun olarak Repository katmanını kullanır.
        
        Args:
            import_id (str): Excel import kaydının ID'si
            project_id (str): Eklenecek proje ID
            
        Returns:
            tuple: (updated_import, error_message)
        """
        try:
            # Repository'yi başlat
            excel_import_repo = ExcelImportRepository()
            
            # Import kaydını al
            import_obj = excel_import_repo.get_by_id(import_id)
            if not import_obj:
                return None, "Import record not found"
                
            # Import'un notlarını güncelle
            notes = import_obj.notes or ""
            if notes and not notes.endswith(" | "):
                notes += " | "
            notes += f"PROJECT_ID:{project_id}"
            
            # Doğrudan modeli güncelleyip kaydedelim
            import_obj.notes = notes
            import_obj.save()
            
            return import_obj, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def _extract_project_id_from_import(excel_import):
        """
        Ortak metod: Excel import kaydından proje ID'yi çıkarır
        
        Args:
            excel_import (ExcelImport): Excel import kaydı
            
        Returns:
            str: Proje ID veya None
        """
        # İlk olarak metadata'dan almayı dene (yeni format)
        if hasattr(excel_import, 'metadata') and excel_import.metadata and isinstance(excel_import.metadata, dict) and 'project_id' in excel_import.metadata:
            project_id = excel_import.metadata.get('project_id')
            return project_id
            
        # Metadata'da yoksa notlardan almayı dene (eski format için geriye uyumluluk)
        if excel_import.notes and "PROJECT_ID:" in excel_import.notes:
            try:
                project_id_part = excel_import.notes.split("PROJECT_ID:")[1].strip()
                if "|" in project_id_part:
                    project_id_part = project_id_part.split("|")[0].strip()
                return project_id_part
            except Exception as e:
                return None
                
        return None
        
    @staticmethod
    def _validate_project(project_id):
        """
        Ortak metod: Proje ID'yi doğrular ve projeyi döndürür
        
        Args:
            project_id (str): Doğrulanacak proje ID'si
            
        Returns:
            tuple: (project, error_message)
        """
        if not project_id:
            return None, None
            
        project_repository = ProjectRepository()
        try:
            project = project_repository.get(id=project_id)
            if not project.is_active:
                return None, "Selected project is not active"
            return project, None
        except Exception as e:
            return None, f"Selected project does not exist: {str(e)}"
            
    @staticmethod
    def _add_item_to_project_inventory(item_id, project_id, quantity, row_index=None):
        """
        Ortak metod: Ürünü proje envanterine ekler
        
        Args:
            item_id (str): Ürün ID'si
            project_id (str): Proje ID'si
            quantity (float): Miktar
            row_index (int, optional): Excel satır indeksi (hata mesajları için)
            
        Returns:
            tuple: (success, error_message)
        """
        if not item_id or not project_id:
            return False, "Missing item_id or project_id"
            
        try:
            # Repository kullanarak proje envanterini güncelle
            project_inventory_repo = ProjectInventoryRepository()
            
            # Proje envanterini kontrol et
            inventory_item = None
            try:
                # Önce ürünü proje envanterinde olup olmadığını kontrol et
                inventory_item = project_inventory_repo.get_project_inventory(project_id, item_id)
            except Exception as e:
                # Proje envanterinde yoksa oluştur
                inventory_item = None
                
            # İlgili envanteri güncelle veya oluştur   
            if inventory_item:
                # Var olan envanter öğesini güncelle
                result = project_inventory_repo.update(
                    inventory_item.id,
                    {
                        'quantity': inventory_item.quantity + quantity
                    }
                )
            else:
                # Yeni envanter öğesi oluştur
                try:
                    result = project_inventory_repo.create(
                        project_id=project_id,
                        item_id=item_id,
                        quantity=quantity,
                        minimum_stock_level=1
                    )
                except Exception as create_err:
                    return False, f"Failed to create inventory: {str(create_err)}"
                
            return True, None
                
        except Exception as e:
            error_msg = f"ERROR adding item to project: {str(e)}"
            return False, error_msg
    
    @staticmethod
    def get_or_create_category_hierarchy(category_path):
        """
        Creates a category hierarchy from a path string like "Electronics > Resistors"
        Limited to only one level of nesting (parent and child).
        Returns the final category in the hierarchy
        
        Args:
            category_path (str): Category path with levels separated by >
            
        Returns:
            Category: The last/deepest category in the hierarchy
        """
        if not category_path:
            return None
            
        categories = [cat.strip() for cat in category_path.split('>')]
        
        # Limit to max 2 levels (parent and child)
        if len(categories) > 2:
            # If more than 2 levels, combine the deeper levels into the child name
            combined_child_name = ' > '.join(categories[1:])
            categories = [categories[0], combined_child_name]
        
        parent = None
        current_category = None
        
        for i, category_name in enumerate(categories):
            if not category_name:
                continue
                
            if parent:
                # We're at the child level
                try:
                    current_category = Category.objects.get(
                        name=category_name, 
                        parent_category=parent
                    )
                except Category.DoesNotExist:
                    # Create a new subcategory
                    current_category = Category.objects.create(
                        name=category_name,
                        parent_category=parent
                    )
            else:
                # We're at the parent level
                try:
                    current_category = Category.objects.get(
                        name=category_name, 
                        parent_category=None
                    )
                except Category.DoesNotExist:
                    # Create a new top-level category
                    current_category = Category.objects.create(
                        name=category_name
                    )
            
            parent = current_category
        
        return current_category
