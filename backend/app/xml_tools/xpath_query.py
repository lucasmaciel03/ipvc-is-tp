"""
XPath and XQuery Support for IPVC Integration System
"""

from lxml import etree
import os
from typing import List, Dict, Any, Optional
from app.core.models import Dataset


class XPathQueryEngine:
    """
    XPath query engine for XML files
    """
    
    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.xml_path = dataset.xml_file_path
        self.tree = None
        self.root = None
        
        if self.xml_path and os.path.exists(self.xml_path):
            self.load_xml()
    
    def load_xml(self):
        """Load XML file into memory"""
        try:
            self.tree = etree.parse(self.xml_path)
            self.root = self.tree.getroot()
            return True
        except Exception as e:
            raise Exception(f"Failed to load XML: {str(e)}")
    
    def execute_xpath(self, xpath_expression: str) -> List[etree.Element]:
        """
        Execute XPath query on the loaded XML
        
        Args:
            xpath_expression: XPath expression to execute
            
        Returns:
            List of matching elements
        """
        if not self.root:
            raise Exception("XML not loaded. Generate XML first.")
        
        try:
            results = self.root.xpath(xpath_expression)
            return results
        except Exception as e:
            raise Exception(f"XPath execution failed: {str(e)}")
    
    def query_to_dict(self, xpath_expression: str) -> List[Dict[str, Any]]:
        """
        Execute XPath and return results as list of dictionaries
        
        Args:
            xpath_expression: XPath expression
            
        Returns:
            List of dictionaries with element data
        """
        results = self.execute_xpath(xpath_expression)
        
        output = []
        for element in results:
            if isinstance(element, etree._Element):
                # Convert element to dict
                item = {}
                
                # Add tag name
                item['_tag'] = element.tag
                
                # Add text content
                if element.text and element.text.strip():
                    item['_text'] = element.text.strip()
                
                # Add attributes
                if element.attrib:
                    item['_attributes'] = dict(element.attrib)
                
                # Add children
                for child in element:
                    if child.text and child.text.strip():
                        item[child.tag] = child.text.strip()
                
                output.append(item)
            else:
                # For text nodes, attributes, etc.
                output.append({'_value': str(element)})
        
        return output
    
    def get_element_text(self, xpath_expression: str) -> List[str]:
        """
        Get text content of elements matching XPath
        
        Args:
            xpath_expression: XPath expression
            
        Returns:
            List of text values
        """
        results = self.execute_xpath(xpath_expression)
        
        texts = []
        for element in results:
            if isinstance(element, etree._Element):
                if element.text:
                    texts.append(element.text.strip())
            else:
                texts.append(str(element))
        
        return texts
    
    def count_elements(self, xpath_expression: str) -> int:
        """
        Count elements matching XPath
        
        Args:
            xpath_expression: XPath expression
            
        Returns:
            Number of matching elements
        """
        results = self.execute_xpath(xpath_expression)
        return len(results)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get XML statistics using XPath
        
        Returns:
            Dictionary with statistics
        """
        if not self.root:
            raise Exception("XML not loaded")
        
        return {
            'root_element': self.root.tag,
            'total_records': self.count_elements('//record'),
            'total_elements': self.count_elements('//*'),
            'depth': self._get_tree_depth(self.root),
        }
    
    def _get_tree_depth(self, element: etree.Element, depth: int = 0) -> int:
        """Calculate XML tree depth"""
        if len(element) == 0:
            return depth
        return max(self._get_tree_depth(child, depth + 1) for child in element)


class XPathQueryExamples:
    """
    Pre-defined XPath query examples
    """
    
    @staticmethod
    def get_examples() -> Dict[str, Dict[str, str]]:
        """Get dictionary of example queries with descriptions"""
        return {
            'all_records': {
                'xpath': '//record',
                'description': 'Select all record elements'
            },
            'first_record': {
                'xpath': '//record[1]',
                'description': 'Select the first record'
            },
            'last_record': {
                'xpath': '//record[last()]',
                'description': 'Select the last record'
            },
            'record_by_position': {
                'xpath': '//record[position() <= 5]',
                'description': 'Select first 5 records'
            },
            'all_field_names': {
                'xpath': '//record[1]/*',
                'description': 'Get all field names from first record'
            },
            'specific_field_values': {
                'xpath': '//record/State_Name/text()',
                'description': 'Get all State_Name values'
            },
            'count_records': {
                'xpath': 'count(//record)',
                'description': 'Count total records'
            },
            'records_with_condition': {
                'xpath': '//record[Area > 1000]',
                'description': 'Records where Area > 1000 (if numeric)'
            },
            'distinct_values': {
                'xpath': '//record/Season[not(. = preceding::Season)]',
                'description': 'Get distinct Season values'
            },
            'nested_query': {
                'xpath': '//record[Crop="Rice"]/State_Name',
                'description': 'Get State names where Crop is Rice'
            }
        }


class XPathQueryBuilder:
    """
    Helper class to build XPath queries programmatically
    """
    
    @staticmethod
    def select_all_records() -> str:
        """XPath to select all records"""
        return '//record'
    
    @staticmethod
    def select_record_by_index(index: int) -> str:
        """XPath to select record by index (1-based)"""
        return f'//record[{index}]'
    
    @staticmethod
    def select_records_range(start: int, end: int) -> str:
        """XPath to select records in range"""
        return f'//record[position() >= {start} and position() <= {end}]'
    
    @staticmethod
    def select_field_values(field_name: str) -> str:
        """XPath to select all values of a specific field"""
        return f'//record/{field_name}/text()'
    
    @staticmethod
    def select_records_where(field_name: str, value: str) -> str:
        """XPath to select records where field equals value"""
        return f'//record[{field_name}="{value}"]'
    
    @staticmethod
    def count_records() -> str:
        """XPath to count records"""
        return 'count(//record)'
    
    @staticmethod
    def count_field_occurrences(field_name: str) -> str:
        """XPath to count occurrences of a field"""
        return f'count(//record/{field_name})'
    
    @staticmethod
    def select_distinct_values(field_name: str) -> str:
        """XPath to get distinct values (approximate)"""
        return f'//record/{field_name}[not(. = preceding::{field_name})]'
    
    @staticmethod
    def select_records_with_condition(condition: str) -> str:
        """XPath to select records matching condition"""
        return f'//record[{condition}]'
    
    @staticmethod
    def select_nested(outer_condition: str, inner_field: str) -> str:
        """XPath for nested queries"""
        return f'//record[{outer_condition}]/{inner_field}'


class XQuerySupport:
    """
    Basic XQuery support using XPath expressions
    Note: Full XQuery requires Saxon or BaseX, this provides XPath-based alternatives
    """
    
    def __init__(self, dataset: Dataset):
        self.xpath_engine = XPathQueryEngine(dataset)
    
    def execute_flwor_like(self, 
                           for_xpath: str,
                           where_condition: Optional[str] = None,
                           return_field: Optional[str] = None) -> List[Any]:
        """
        Execute FLWOR-like query using XPath
        
        FLWOR = For-Let-Where-Order-Return (XQuery syntax)
        This provides a simplified version using XPath
        
        Args:
            for_xpath: XPath expression for the 'for' clause
            where_condition: Optional condition for filtering
            return_field: Optional field to return
            
        Returns:
            List of results
        """
        # Build XPath expression
        xpath = for_xpath
        
        if where_condition:
            # Add where clause
            if '[' in xpath:
                # Insert condition before existing predicate
                xpath = xpath.replace('[', f'[{where_condition} and ', 1)
            else:
                xpath = f'{xpath}[{where_condition}]'
        
        if return_field:
            # Add return field
            xpath = f'{xpath}/{return_field}'
        
        return self.xpath_engine.query_to_dict(xpath)
    
    def aggregate(self, field_xpath: str, operation: str) -> Any:
        """
        Perform aggregate operations
        
        Args:
            field_xpath: XPath to numeric field
            operation: 'sum', 'avg', 'min', 'max', 'count'
            
        Returns:
            Aggregated value
        """
        values = self.xpath_engine.get_element_text(field_xpath)
        
        # Try to convert to numbers
        try:
            numeric_values = [float(v) for v in values if v]
        except ValueError:
            raise Exception("Field values are not numeric")
        
        if operation == 'count':
            return len(numeric_values)
        elif operation == 'sum':
            return sum(numeric_values)
        elif operation == 'avg':
            return sum(numeric_values) / len(numeric_values) if numeric_values else 0
        elif operation == 'min':
            return min(numeric_values) if numeric_values else None
        elif operation == 'max':
            return max(numeric_values) if numeric_values else None
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def group_by(self, group_field: str, aggregate_field: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate GROUP BY using XPath
        
        Args:
            group_field: Field to group by
            aggregate_field: Optional field to aggregate
            
        Returns:
            Dictionary with grouped results
        """
        # Get distinct values of group field
        distinct_xpath = XPathQueryBuilder.select_distinct_values(group_field)
        distinct_values = self.xpath_engine.get_element_text(distinct_xpath)
        
        results = {}
        for value in distinct_values:
            if not value:
                continue
            
            # Count records for this value
            count_xpath = f'count(//record[{group_field}="{value}"])'
            count = self.xpath_engine.execute_xpath(count_xpath)
            
            results[value] = {
                'count': int(count[0]) if count else 0
            }
            
            # If aggregate field specified, calculate aggregates
            if aggregate_field:
                value_xpath = f'//record[{group_field}="{value}"]/{aggregate_field}/text()'
                values = self.xpath_engine.get_element_text(value_xpath)
                
                try:
                    numeric_values = [float(v) for v in values if v]
                    if numeric_values:
                        results[value]['sum'] = sum(numeric_values)
                        results[value]['avg'] = sum(numeric_values) / len(numeric_values)
                        results[value]['min'] = min(numeric_values)
                        results[value]['max'] = max(numeric_values)
                except ValueError:
                    pass
        
        return results
