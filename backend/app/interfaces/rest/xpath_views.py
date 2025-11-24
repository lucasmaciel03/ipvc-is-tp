"""
REST API Views for XPath/XQuery functionality
"""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404

from app.core.models import Dataset
from app.xml_tools.xpath_query import (
    XPathQueryEngine, 
    XPathQueryExamples, 
    XPathQueryBuilder,
    XQuerySupport
)


class XPathQueryViewSet(viewsets.ViewSet):
    """
    ViewSet for XPath/XQuery operations on datasets
    """
    
    def list(self, request):
        """List available XPath query examples"""
        examples = XPathQueryExamples.get_examples()
        return Response({
            'message': 'Available XPath query examples',
            'examples': examples,
            'builders': {
                'select_all': 'Use XPathQueryBuilder.select_all_records()',
                'select_by_index': 'Use XPathQueryBuilder.select_record_by_index(index)',
                'select_field': 'Use XPathQueryBuilder.select_field_values(field_name)',
                'count': 'Use XPathQueryBuilder.count_records()',
            }
        })
    
    @action(detail=False, methods=['post'])
    def execute(self, request):
        """
        Execute custom XPath query
        
        POST /api/xpath/execute/
        {
            "dataset_id": 1,
            "xpath": "//record[1]",
            "format": "dict"  // or "text" or "count"
        }
        """
        dataset_id = request.data.get('dataset_id')
        xpath_expr = request.data.get('xpath')
        output_format = request.data.get('format', 'dict')
        
        if not dataset_id or not xpath_expr:
            return Response(
                {'error': 'dataset_id and xpath are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dataset = get_object_or_404(Dataset, id=dataset_id)
            xpath_engine = XPathQueryEngine(dataset)
            
            if output_format == 'text':
                results = xpath_engine.get_element_text(xpath_expr)
            elif output_format == 'count':
                results = xpath_engine.count_elements(xpath_expr)
            else:  # dict
                results = xpath_engine.query_to_dict(xpath_expr)
            
            return Response({
                'dataset': dataset.name,
                'xpath': xpath_expr,
                'format': output_format,
                'results': results,
                'count': len(results) if isinstance(results, list) else 1
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def statistics(self, request):
        """
        Get XML statistics for a dataset
        
        POST /api/xpath/statistics/
        {
            "dataset_id": 1
        }
        """
        dataset_id = request.data.get('dataset_id')
        
        if not dataset_id:
            return Response(
                {'error': 'dataset_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dataset = get_object_or_404(Dataset, id=dataset_id)
            xpath_engine = XPathQueryEngine(dataset)
            stats = xpath_engine.get_statistics()
            
            return Response({
                'dataset': dataset.name,
                'statistics': stats
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def aggregate(self, request):
        """
        Perform aggregate operations
        
        POST /api/xpath/aggregate/
        {
            "dataset_id": 1,
            "field": "Area",
            "operation": "sum"  // sum, avg, min, max, count
        }
        """
        dataset_id = request.data.get('dataset_id')
        field = request.data.get('field')
        operation = request.data.get('operation', 'count')
        
        if not dataset_id or not field:
            return Response(
                {'error': 'dataset_id and field are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dataset = get_object_or_404(Dataset, id=dataset_id)
            xquery = XQuerySupport(dataset)
            
            field_xpath = f'//record/{field}/text()'
            result = xquery.aggregate(field_xpath, operation)
            
            return Response({
                'dataset': dataset.name,
                'field': field,
                'operation': operation,
                'result': result
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def group_by(self, request):
        """
        Group by field with optional aggregation
        
        POST /api/xpath/group_by/
        {
            "dataset_id": 1,
            "group_field": "Season",
            "aggregate_field": "Area"  // optional
        }
        """
        dataset_id = request.data.get('dataset_id')
        group_field = request.data.get('group_field')
        aggregate_field = request.data.get('aggregate_field')
        
        if not dataset_id or not group_field:
            return Response(
                {'error': 'dataset_id and group_field are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dataset = get_object_or_404(Dataset, id=dataset_id)
            xquery = XQuerySupport(dataset)
            
            results = xquery.group_by(group_field, aggregate_field)
            
            return Response({
                'dataset': dataset.name,
                'group_field': group_field,
                'aggregate_field': aggregate_field,
                'results': results,
                'groups_count': len(results)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        Execute FLWOR-like query
        
        POST /api/xpath/query/
        {
            "dataset_id": 1,
            "for": "//record",
            "where": "Area > 1000",  // optional
            "return": "State_Name"   // optional
        }
        """
        dataset_id = request.data.get('dataset_id')
        for_clause = request.data.get('for', '//record')
        where_clause = request.data.get('where')
        return_field = request.data.get('return')
        
        if not dataset_id:
            return Response(
                {'error': 'dataset_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dataset = get_object_or_404(Dataset, id=dataset_id)
            xquery = XQuerySupport(dataset)
            
            results = xquery.execute_flwor_like(
                for_xpath=for_clause,
                where_condition=where_clause,
                return_field=return_field
            )
            
            return Response({
                'dataset': dataset.name,
                'query': {
                    'for': for_clause,
                    'where': where_clause,
                    'return': return_field
                },
                'results': results,
                'count': len(results)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
