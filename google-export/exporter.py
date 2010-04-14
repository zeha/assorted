import gdata.docs.service
import gdata.spreadsheet.service

app_name = 'at.zeha.google-export-v0-github'
login_u = 'username@example.org'
login_p = 'password'
export_folder = '/home/username/google-export/data/'



gd_client = gdata.docs.service.DocsService(source=app_name)
gd_client.ClientLogin(login_u, login_p)
gs_client = gdata.spreadsheet.service.SpreadsheetsService(source=app_name)
gs_client.ClientLogin(login_u, login_p)


documents_feed = gd_client.GetDocumentListFeed()
for document_entry in documents_feed.entry:
  file_path = export_folder + document_entry.title.text
  docs_token = gd_client.GetClientLoginToken()

  resource_id = document_entry.resourceId.text
  res_type = resource_id[:resource_id.find(':')]
  if res_type == 'spreadsheet':
    file_path = file_path + '.ods'
    gd_client.SetClientLoginToken(gs_client.GetClientLoginToken())
  else:
    file_path = file_path + '.odt'

  gd_client.Export(resource_id, file_path)
  gd_client.SetClientLoginToken(docs_token)



