"""
Views for the core application
"""
from django.shortcuts import render
from django.http import JsonResponse
from app.core.models import Dataset, DataRecord


def index(request):
    """
    Dashboard homepage showing all datasets
    """
    datasets = Dataset.objects.all().order_by('-created_at')
    
    # Calculate total statistics
    total_datasets = datasets.count()
    total_records = DataRecord.objects.count()
    total_rows = sum(ds.total_rows for ds in datasets)
    
    context = {
        'datasets': datasets,
        'total_datasets': total_datasets,
        'total_records': total_records,
        'total_rows': total_rows,
    }
    
    return render(request, 'core/index.html', context)


def dataset_detail(request, dataset_id):
    """
    Dataset detail view
    """
    from django.shortcuts import get_object_or_404
    
    dataset = get_object_or_404(Dataset, id=dataset_id)
    columns = dataset.columns.all()
    records = dataset.records.all()[:100]  # Show first 100 records
    
    context = {
        'dataset': dataset,
        'columns': columns,
        'records': records,
    }
    
    return render(request, 'core/dataset_detail.html', context)
