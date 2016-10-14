from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'front.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^book/','dashboard.book.show'),
    #url(r'^index/','dashboard.views.index'),
    url(r'^$','dashboard.views.index'),
    url(r'^detail/(hangzhou|nanjing|shanghai|tucheng|beijing)/$','dashboard.views_detail.show'),
    url(r'^test_index/','dashboard.test_views.index'),
    url(r'^test_detail/(hangzhou|nanjing|shanghai|tucheng|beijing)/$','dashboard.test_views_detail.show'),
    url(r'^download/','dashboard.download.index'),
    url(r'^open/','dashboard.open.index'),
    url(r'^index_open/','dashboard.index_open.index'),
    url(r'^um_open','dashboard.um_open.index'),
    url(r'^show_instance','dashboard.show_instance.index'),       
    url(r'^add/$','dashboard.handle_ajax.add'),        
    url(r'^ajax_instance/$','dashboard.handle_ajax.ajax_instance'),        
    url(r'^ajax_machine/$','dashboard.handle_ajax.ajax_machine'),        
    url(r'^ajax_kpi/$','dashboard.handle_ajax.ajax_kpi'),        
    url(r'^ajax_index_machine/$','dashboard.handle_ajax.ajax_index_machine'),        
    url(r'^ajax_index_instance/$','dashboard.handle_ajax.ajax_index_instance'),        
    url(r'^ajax_new_fault/$','dashboard.handle_ajax.ajax_new_fault'),        
    url(r'^test_ajax_new_fault/$','dashboard.handle_ajax.test_ajax_new_fault'),        
    url(r'^ajax_detail_package/$','dashboard.handle_ajax.ajax_detail_package'),        
    url(r'^ajax_detail_ltr/$','dashboard.handle_ajax.ajax_detail_ltr'),        
    url(r'^ajax_detail_base/$','dashboard.handle_ajax.ajax_detail_base'),        
    url(r'^ajax_detail_um/$','dashboard.handle_ajax.ajax_detail_um'),        
    url(r'^ajax_detail_machine/(hangzhou|nanjing|shanghai|tucheng|beijing)/$','dashboard.handle_ajax.ajax_detail_machine'),      
    url(r'^ajax_detail_instance/(hangzhou|nanjing|shanghai|tucheng|beijing)/$','dashboard.handle_ajax.ajax_detail_instance'),
    url(r'^ajax_detail_agent/(hangzhou|nanjing|shanghai|tucheng|beijing)/$','dashboard.handle_ajax.ajax_detail_agent'),        
    url(r'^ajax_show_instance/$','dashboard.handle_ajax.ajax_show_instance'),        
)