# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from akorn.couch import db_store, db_journals
from akorn.celery.scrapers import tasks

def backend_journals(request):
  db_docs = db_store
  
  journals = [db_journals[doc_id] for doc_id in db_journals if '_design' not in doc_id]

  journals = sorted(journals, key=lambda doc: doc['name'])

  for journal in journals:
    journal.num_docs = len(db_docs.view('index/journal_id', key=journal.id, include_docs=False).rows)

  return render_to_response('backend/journals.html', {'journals': journals,}, context_instance=RequestContext(request))

def backend_journal(request, journal_id):
  db_docs = db_store 
  journal_doc = db_journals[journal_id]

  rows = db_docs.view('index/journal_id', key=journal_id, include_docs=True).rows

  num_rescrape = 0
  scraper_modules = set()
  
  docs = [row.doc for row in rows]

  for row in rows:
    doc = row.doc
    if 'rescrape' in doc and doc['rescrape']:
      num_rescrape += 1
   
    if 'scraper_module' in doc:
      scraper_modules.add(doc['scraper_module'])

  return render_to_response('backend/journal.html', {'journal': journal_doc,
                                                     'docs': docs,
                                                     'num_rescrape': num_rescrape,
                                                     'scraper_modules': list(scraper_modules),},
                            context_instance=RequestContext(request))

def rescrape_doc(doc_id):
  doc = db_store[doc_id]

  doc['currently_rescraping'] = True
  db_store.save(doc)

  if 'source_url' in doc:
    print doc['source_url']
    tasks.scrape_journal.delay(doc['source_url'], doc.id)
  elif 'source_urls' in doc:
    print doc['source_urls']
    tasks.scrape_journal.delay(doc['source_urls'][0], doc.id)
  elif 'scraper_source' in doc:
    print doc['scraper_source']
    tasks.scrape_journal.delay(doc['scraper_source'], doc.id)

def backend_scrapers(request):
  if request.method == "POST":
    docs_to_rescrape = [b for a in request.POST.getlist('to_rescrape') for b in a.split(',')]
    
    for doc in docs_to_rescrape:
      rescrape_doc(doc)

  in_progress = {'num': 0}
  for row in db_store.view('rescrape/currently_rescraping', group=True).rows:
    in_progress['num']=row['value']

  scraper_details = {}
  
  for row in db_store.view('rescrape/scraper_exception_errors').rows:
    module, error = row['key']
    error = error.split(":")[0]
    scraper_details.setdefault(module, 
                               { 'name': module.split('.')[-1],
                                 'module': module,
                                 'num_docs': 0,
                                 'errors': {}})
    scraper_details[module]['errors'].setdefault(error, {'num_rescrape': 0, 'ids':[]})
    scraper_details[module]['errors'][error]['num_rescrape'] += 1
    scraper_details[module]['errors'][error]['ids'].append(row['id'])
    
  for row in db_store.view('rescrape/scraper_total_docs', group=True):
    module = row['key']
    if module in scraper_details:
      scraper_details[module]['num_docs'] = row['value']

  scrapers = []
  for key, details in scraper_details.items():
    errors = []
    for exception, error_details in details['errors'].items():
      errors.append({'exception':exception, 
                     'num_rescrape':error_details['num_rescrape'], 
                       'ids':u",".join(error_details['ids']),})
      
    scrapers.append({'name':details['name'],
                     'module':details['module'],
                     'num_docs':details['num_docs'],
                     'error_type_count':len(details['errors']),
                     'errors': errors})

  return render_to_response( 'backend/scrapers.html', 
                             {'scrapers': scrapers,
                              'in_progress': in_progress,}, 
                             context_instance=RequestContext(request) )
