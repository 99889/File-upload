from django.shortcuts import render
from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd

def handle_uploaded_file(f):
    if f.name.endswith('.xlsx'):
        df = pd.read_excel(f)
    elif f.name.endswith('.csv'):
        df = pd.read_csv(f)
    else:
        raise ValueError("Unsupported file type")
    
    # Normalize column names by stripping and converting to lowercase
    df.columns = df.columns.str.strip().str.lower()
    
    required_columns = {'cust state', 'dpd'}
    if not required_columns.issubset(df.columns):
        missing_cols = required_columns - set(df.columns)
        raise ValueError(f"Missing columns in uploaded file: {', '.join(missing_cols)}")
    
    summary = df.groupby(['cust state', 'dpd']).size().reset_index(name='Count')
    return summary

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = UploadedFile(file=request.FILES['file'])
            uploaded_file.save()
            try:
                summary = handle_uploaded_file(request.FILES['file'])
                return render(request, 'fileupload/summary.html', {'summary': summary.to_html(index=False)})
            except ValueError as e:
                return render(request, 'fileupload/upload.html', {'form': form, 'error': str(e)})
    else:
        form = UploadFileForm()
    return render(request, 'fileupload/upload.html', {'form': form})
