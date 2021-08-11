# return data
from django import utils
from django.shortcuts import render
# download file
from django.http import FileResponse , JsonResponse
# return html
from django.views.decorators.clickjacking import xframe_options_exempt
# return Json , csv , shlex , subprocess , logging , os , sys , platform , shutil , stat , base64
import json , csv , shlex , subprocess , logging , os , sys , platform , shutil , stat , base64
from django.views.decorators.csrf import csrf_exempt
# time
from django.utils import timezone
# database tables
from thedataset import models
# page helper
from django.core.paginator import Paginator
# serializers
from django.core import serializers
#
from django.views import View 
#csv to json
sys.path.append("..") 
import util

# 分页
# 查询数据库
from django.db import connection, connections
# 查询数据库结果转字典。
from django.forms.models import model_to_dict
                            #需要更改的路径如下**************************************************************************
backend_engine_linux = '/../textoir/open_intent_detection/run.py '
backend_engine_win = '\\..\\textoir\\run_detect.py '

@xframe_options_exempt
def model_management(request):
    return render(request,'detection/model-list.html')


@csrf_exempt
def getModelList(request):
    model_name_select = request.GET.get('model_name_select')
    page = request.GET.get('page')
    limit = request.GET.get("limit")

    if model_name_select == None:
        model_name_select = ''
    
    modelList = models.Model_Tdes.objects.values().filter(model_name__contains=model_name_select,type=1).order_by('model_id')
    count = modelList.count()
    # 分页
    paginator = Paginator(modelList, limit)
    modelList = paginator.get_page(page)

    result = {}
    result['code'] = 0
    result['msg'] = ''
    result['count'] = count
    result['data'] = list(modelList)
    
    return JsonResponse(result)

@xframe_options_exempt
def model_management_details(request):
    model_id = request.GET.get('model_id')
    # print(model_id)
    obj = models.Model_Tdes.objects.get(model_id=model_id)
    # obj_param = models.Hyper_parameters.objects.get(model_id = model_id)
    paramList = models.Hyper_parameters.objects.filter(model_id=model_id)
    return render(request,'detection/model-details.html',{'obj':obj,'paramList':paramList})


@xframe_options_exempt
def model_training(request):
    return render(request,'detection/model-training-log-list.html')


@xframe_options_exempt
def getModelLogList(request):                                        #查询所有Model Training 数据
    type_select = request.GET.get('type_select')
    dataset_select = request.GET.get("dataset_select")
    model_select = request.GET.get("model_select")
    page = request.GET.get('page')
    limit = request.GET.get("limit")

    
    logList = models.Run_Log.objects.values().filter(model_id__type=1)

    if dataset_select == None:
        dataset_select = ''
    if model_select == None:
        model_select = ''
    logList = logList.filter(dataset_name__contains=dataset_select,model_name__contains=model_select).order_by('-log_id')
    if type_select != '5':
        logList = logList.filter(type=type_select)

    # 分页
    paginator = Paginator(logList, limit)
    logList = paginator.get_page(page)
    count = paginator.count

    result = {}
    result['code'] = 0
    result['msg'] = ''
    result['count'] = count
    result['data'] = list(logList)
    return JsonResponse(result)

@xframe_options_exempt
def toLogParameter(request):
    log_id = request.GET.get('log_id')
    paramList = models.run_log_hyper_parameters.objects.filter(log_id=log_id)
    ex_data = models.Run_Log.objects.values().filter(log_id=log_id)
    return render(request,'detection/model-training-log-parameter.html',{'model_id': log_id,'paramList':paramList,'ex_data':ex_data})

@xframe_options_exempt
def toRunModel(request):
    
    # get model list
    modelList = models.Model_Tdes.objects.values().filter(type=1)
    datasetList = models.DataSet.objects.values()

    result = {}
    result['modelList'] = modelList
    result['datasetList'] = datasetList
    
    return render(request,'detection/model-training-log-torun.html', result)


@csrf_exempt
def getParamListByModelId(request): #点击ADD，跑模型前，选择模型后，查询（最好的？）超参数----------------------------------------------------------------
    model_id_select = request.GET.get('model_select')

    if model_id_select == None:
        return JsonResponse({'code':0,'msg':'','count':0,'data':[]})
    
    resultList = models.Hyper_parameters.objects.values().filter(model_id=model_id_select).order_by('param_id')
    
    paginator = Paginator(resultList, 100)
    resultList = paginator.get_page(1)

    result = {}
    result['code'] = 0
    result['msg'] = ''
    result['count'] = paginator.count
    result['data'] = list(resultList)
    return JsonResponse(result)

@csrf_exempt
def add_model_training_log(request):    #点击run添加参数，跑模型------ -------------------------------------------------------------------------
    #将模型的参数列表直接读取出来得到参数列表和参数的数量
    print('there is add_model_training_log')
    model_id = request.POST['model_id']
    dataset_name_select = request.POST['dataset_name_select']
    Known_Intent_Ratio = request.POST['Known_Intent_Ratio']
    Annotated_Ratio = request.POST['Annotated_Ratio']
    params = request.POST['params']
    paramsListJson = json.loads(params)

    modelItem = models.Model_Tdes.objects.get(model_id=model_id)
    model_name = modelItem.model_name 
    print("*"*20)
    print(model_name)
    print("*"*20+"\n")    
    # 拼接命令
    para_str_python = ' --dataset '+  dataset_name_select + ' --known_cls_ratio ' + Known_Intent_Ratio + ' --labeled_ratio ' + Annotated_Ratio + ' --method ' + model_name +' --save_model'+ ' --train'    #before#for paramItem in paramsListJson:
    #before#    para_str_python = para_str_python + ' --' + paramItem['param_name'] + ' ' + paramItem['default_value']
        # print('param_id==',paramItem['param_id'],'\tparam_name==',paramItem['param_name'],'\tdefault_value==',paramItem['default_value'],'\trun_value==',paramItem['run_value'])
    print('para_str_python==',para_str_python)
    # 生成本地路径
    ## genernate local_path
    print('local_path===',sys.path[0])      #需要更改的路径如下***************************************************************************
    if platform.system() == 'Linux':
        local_path = sys.path[0]+'/static/log/detection/add_model_training_log/running/'+  dataset_name_select + model_id + Annotated_Ratio + Known_Intent_Ratio +'/'
    elif platform.system() == 'Windows':
        local_path = sys.path[0]+'\\static\\log\\detection\\add_model_training_log\\running\\'+  dataset_name_select + model_id + Annotated_Ratio + Known_Intent_Ratio +'\\'
    ## determine if the dataset exists
    if os.path.exists(local_path):
        return JsonResponse({'code':201,'msg':'The  Process Already Exists , Please Check It !!!'})

    try:
        run_logItem = models.Run_Log(                         
            dataset_name = dataset_name_select, 
            model_name = modelItem.model_name,
            model_id_id = model_id,
            Local_Path = local_path, 
            create_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            Annotated_ratio = Annotated_Ratio, 
            Intent_Ratio = Known_Intent_Ratio,
            type = 1 # runing state
            
            )
        run_logItem.save()
        # save msg to run_log_hyper_parameters
        for paramItem in paramsListJson:
            run_log_hyper_parametersItem = models.run_log_hyper_parameters(
                    param_name = paramItem['param_name'],param_describe = paramItem['param_describe'],
                    value_type = paramItem['value_type'],default_value = paramItem['default_value'],
                    run_value = paramItem['default_value'],log_id = run_logItem.log_id
                )
            run_log_hyper_parametersItem.save()

        os.makedirs(local_path)

        print('*'*20, '\n\npara_str_python:', para_str_python, '\n\n')
        str_run = ''
        if platform.system() == 'Linux':
            str_run = 'python ' + sys.path[0]+ backend_engine_linux +  para_str_python +'--log_id'+run_logItem.log_id #最终执行跑模型命令语句————-——————————————————————————————————————
            print('208: ',str_run)
        elif platform.system() == 'Windows':
            str_run = 'python ' + sys.path[0]+ backend_engine_win + para_str_python
        
        print('*'*20, '\n\nstr_run:', str_run, '\n\n')
        # run model
        str_run = shlex.split(str_run)
        process = subprocess.Popen(str_run)
        # #get pid
        run_pid = process.pid
        # run_pid = 99999   ## 测试用
        ## save msg to run log
        updat = models.Run_Log.objects.filter(log_id=run_logItem.log_id).update(run_pid = run_pid)
        
        
        ##get returncode ---wait runing state change
        process.communicate()
        run_type = process.returncode
        # run_type = 0  ## 测试用
        # ## save run_type to run log
        # 1--runing  2--finished 3--failed
        if run_type == 0 or run_type == '0':
            type_after = 2
        else :
            type_after = 3
        # update runing state to run_log
        updat = models.Run_Log.objects.filter(log_id=run_logItem.log_id).update(run_pid = run_pid,type=type_after)

    except :
        updat = models.Run_Log.objects.filter(log_id=run_logItem.log_id).update(type=3)
        return JsonResponse({'code': 400, 'msg': 'Run  Process Has An Error ！！'})
    finally:
        if os.path.exists(local_path):
            os.removedirs(local_path)
    print("运行完毕")
    #print (os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    #utils.csv_to_json()
    dataset_path=os.path.abspath(os.path.join(os.getcwd(), "../.."))
    
    datafile2 = os.path.join(dataset_path, 'TEXTOIR/frontend/results/results_final.csv')
    datafile1 = os.path.join(dataset_path, 'TEXTOIR/frontend/detection/result_json/result.json')
    util.csv2json(datafile2,datafile1)
    return JsonResponse({'code':200,'msg':'Successfully Running Process!'})


#kill_run
#need pid and stop
@csrf_exempt
def kill_running(request):
    try:
        run_pid = request.POST.get('run_pid')
        log_id = request.POST.get('log_id')
        if models.Run_Log.objects.get(log_id=log_id).type != 1:
            return JsonResponse({'code': 400, 'msg': 'Process '+run_pid+' Was Over ！！'})
        command = 'kill -9 ' + str(run_pid)
        command = shlex.split(command)
        subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        updat = models.Run_Log.objects.filter(log_id=log_id).update(type=3)
        os.removedirs(models.Run_Log.objects.get(log_id=log_id).Local_Path)
        print("there is pid333")
    except:
        return JsonResponse({'code': 400, 'msg': 'Kill  Process Has An Error ！！'})
    return JsonResponse({'code':200,'msg':'Successfully Kill Process!'})

@xframe_options_exempt
def model_test(request):
    print("----------------------------***-------------------------------")
    datasetList = models.DataSet.objects.values()
    modelList_detection = models.Model_Tdes.objects.values().filter(type = 1)

 

    if request.GET.get('log_id'):     #如果是跳转，带着log_id_jump
        log_id = request.GET.get('log_id')
        create_time_new = models.Run_Log.objects.values().filter(log_id = log_id,model_id__type=1).first()#,type = 2)     #默认显示最新的一条
    else:
        create_time_new = models.Run_Log.objects.values().filter(model_id__type=1).order_by('-log_id').first()#,type = 2)     #默认显示最新的一条
        log_id = create_time_new['log_id']
    
    
     
    dataset_new = create_time_new['dataset_name']
    model_new = create_time_new['model_name']
    create_time = models.Run_Log.objects.values().filter(dataset_name = dataset_new,model_name=model_new,model_id__type=1)#,type = 2) #成功完成的记录 *******待改***********

    parameters = models.run_log_hyper_parameters.objects.values().filter(log_id=log_id)
  


    
   
    print("-------------------------------***----------------------------")
    result = {}
    result['datasetList'] = datasetList
    result['modelList_detection'] = modelList_detection
    result['create_time'] = create_time
    result['create_time_new'] = create_time_new
    result['parameters'] = parameters
    
    return render(request,'detection/model-test.html' , result)


@csrf_exempt 
def check_evaluation(request):
    #print("-------------------****-----------------")
    #log_id= request.POST['log_id']
    log_id= request.GET.get('log_id')
    
    
    modelList = models.Run_Log.objects.values().filter(log_id=log_id)
    result = list(modelList)
   
 
    #return render(request,'detection/model-test.html' , result)  {'obj':obj,'paramList':paramList}
    return JsonResponse({'code':200,'msg':'Successfully !','data':result})
    #return render(request,'detection/model-test.html' )
@csrf_exempt 
def show_create_time(request):
  
    
    dataset_name= request.GET.get('dataset_name')
    model_name= request.GET.get('model_name')
    if(dataset_name) == None:
        dataset_name_default = "Dataset"
    dataset_name_default =dataset_name
    if(model_name) == None:
        model_name_default = "Open Intent Detection"
    model_name_default = model_name
    
    create_time = models.Run_Log.objects.values().filter(dataset_name=dataset_name,model_name=model_name).order_by('-log_id')
    create_time_new = models.Run_Log.objects.values().first()#.filter(type = 2)
    #result = list(create_time_result)
  
    #return render(request,'detection/model-test.html' , result)  {'obj':obj,'paramList':paramList}
    #return JsonResponse({'code':200,'msg':'Successfully !','data':result})
 
    datasetList = models.DataSet.objects.values()
    modelList_detection = models.Model_Tdes.objects.values().filter(type = 1)
    result = {}
    result['datasetList'] = datasetList
    result['dataset_name_default'] = dataset_name_default
    result['modelList_detection'] = modelList_detection
    result['model_name_default'] = model_name_default
    result['create_time'] = create_time

    result = list(create_time)
    #return render(request,'detection/model-test.html' , result)
    return JsonResponse({'code':200,'msg':'Successfully !','data':result})
    #return render(request,'detection/model-test.html' )
@csrf_exempt 
def show_hyper_parameters(request):
  
    
    log_id= request.GET.get('log_id')

    #return render(request,'detection/model-test.html' , result)  {'obj':obj,'paramList':paramList}
    #return JsonResponse({'code':200,'msg':'Successfully !','data':result})
 
    parameters = models.run_log_hyper_parameters.objects.values().filter(log_id=log_id)
    result = {}

    result = list(parameters)
    #return render(request,'detection/model-test.html' , result)
    return JsonResponse({'code':200,'msg':'Successfully !','data':result})
    #return render(request,'detection/model-test.html' )
    
@csrf_exempt    #********************************************************************************************未看
def getModelAnalysisExampleData(request):
    def read(path):
        reader = csv.reader(open(path), delimiter = '\t', quotechar = None)
        lines = []
        for i,j in enumerate(reader):
            if i == 0 :
                continue
            lines.append(j[0]+'\n')
        return lines
    ##get base msg
    example_num = request.POST['example_num']
    str_path = ''
    if example_num == 'Example-1':
        str_path = 'test1_data'
    elif example_num == 'Example-2':
        str_path = 'test2_data'
    elif example_num == 'Example-3':
        str_path = 'test3_data'
    ## genernate local_path
    local_path = ''
    if platform.system() == 'Linux':
        local_path = sys.path[0]+'/static/test_data/test_data/'+  str_path + '/test.tsv'
    elif platform.system() == 'Windows':
        local_path = sys.path[0]+'\\static\\test_data\\test_data\\'+  str_path + '\\test.tsv'
    ##
    text = read(local_path)
    ## return msg
    return JsonResponse({'code':200,'msg':'Successfully Add Dataset','text':text})


@csrf_exempt
def modelAnalysisTest(request):
    model_detection = request.POST['model_detection']
    example_select_detection = request.POST['example_select_detection']

  

    # #使用训好的模型预测
    # str1 = model_detection 
    # str2 = example_select_detection
    # if str1 == None or str1 =='' or str1 == 'New Intent Detection':
    #     pass
    # else:
    #     comend = 'python /home/lxt/tdes/model/'+str1+'/model_predict.py'+" --examples_path "+str2

    #     print("&"*10)
    #     print(comend)
    #     print("&"*10)

    #     #model_predict
    #     comend = shlex.split(comend)
    #     process = subprocess.Popen(comend)
    #     #根据本地result文件更新结果
    #     result_path = '/home/lxt/tdes/model/'+str1+'/pred_result/result.txt'

    #     result = []
    #     with open(result_path,'r') as f:
    #         for line in f.readlines():
    #             data = line.split('\t\n')
    #             for strs in data:
    #                 sub_str = strs.split('\t')
    #             if sub_str:
    #                 result.append(sub_str)
    #         # print(result[0][2].replace('\n',''))
        
    #     print('there is insert_after_begin')
    #     for i,j in enumerate(result):
    #         sents = j[0]
    #         pred = j[1]
    #         models.Model_Test_Example.objects.filter(sentences = sents).update(predict_result = pred)

    return JsonResponse({'code':200,'msg':'Successfully Detection The Intent!'})



@xframe_options_exempt
def model_analysis(request):#
    dataset_list = models.DataSet.objects.values()
    modelList_detection = models.Model_Tdes.objects.values().filter(type = 1)
    example_list = models.Model_Test_Example.objects.values()


    if request.GET.get('log_id'):     #如果是跳转，带着log_id_jump
        log_id = request.GET.get('log_id')
        create_time_new = models.Run_Log.objects.values().filter(log_id = log_id,model_id__type=1).first()#.filter(type = 2)     #默认显示最新的一条
    else:
        create_time_new = models.Run_Log.objects.values().filter(model_id__type=1).order_by('-log_id').first()#.filter(type = 2)     #默认显示最新的一条
        log_id = create_time_new['log_id']

    dataset_new = create_time_new['dataset_name']
    model_new = create_time_new['model_name']
    create_time = models.Run_Log.objects.values().filter(dataset_name = dataset_new,model_name=model_new,model_id__type=1) #type=2#成功完成的记录 *******待改***********


    result = {}
    result['dataset_list'] = dataset_list
    result['modelList_detection'] = modelList_detection
    result['exampleList'] = example_list
    result['create_time'] = create_time
    result['create_time_new'] = create_time_new
    
    return render(request,'detection/model-analysis.html',result)


@csrf_exempt
def model_evaluation_getDataOfTFOverallByKey(request):
    key = request.GET.get('key')
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'true_false_overall.json')
    data_iokir = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_iokir = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_iokir
    return JsonResponse(results)

@csrf_exempt
def model_evaluation_getDataOfTFOverallByKey_new(request):
    key = request.GET.get('key')
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'true_false_overall_new.json')
    data_iokir = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_iokir = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_iokir
    return JsonResponse(results)


@csrf_exempt
def model_evaluation_getDataOfTFFineByKey(request):
    key = request.GET.get('key')
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'true_false_fine.json')
    data_iokir = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_iokir = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_iokir
    return JsonResponse(results)

@csrf_exempt
def model_evaluation_getDataOfTFFineByKey_new(request):
    key = request.GET.get('key')
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'true_false_fine_new.json')
    data_iokir = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_iokir = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_iokir
    return JsonResponse(results)


@csrf_exempt
def model_evaluation_getDataOfIOKIRByKey(request):
    key = request.GET.get('key')
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'json_detection_IOKIR.json')
    data_iokir = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_iokir = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_iokir
    return JsonResponse(results)
@csrf_exempt
def model_evaluation_getDataOfIOKIRByKey_new(request):
    key = request.GET.get('key')
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'json_detection_loss.json')
    print("*******************************************")
    print(key)
    print(json_path)
    #/home/wx/workplace_1/TEXTOIR/frontend/static/jsons/open_intent_detection/json_detection_IOKIR.json
    print("*******************************************")
    data_iokir = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_iokir = load_dict[key]
    
    results = {}
    results['code'] = 201
    results['msg'] = ''
    results['data'] = data_iokir
    return JsonResponse(results)

@csrf_exempt
def model_evaluation_getDataOfIOLRByKey(request):
    key = request.GET.get('key')
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'json_detection_IOLR.json')
    data_iokir = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_iokir = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_iokir
    return JsonResponse(results)
@csrf_exempt
def model_evaluation_getDataOfIOLRByKey_new(request):
    key = request.GET.get('key')
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'json_detection_metric.json')
    data_iokir = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_iokir = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_iokir
    return JsonResponse(results)


@csrf_exempt
def model_analysis_getClassListByDatasetNameAndMethod(request):
    print('model_analysis_getTableResultsByDatasetNameAndMethod')
    dataset_name = request.GET.get('dataset_name')
    method = request.GET.get('method')
    log_id = request.GET.get('log_id')#new
    class_type = 'known'
    page = request.GET.get('page')
    limit = request.GET.get("limit")
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'analysis_table_info_new.json')
    return_list = []
    print("*"*15)
    print("class_list_"+ dataset_name +'_'+ method +"_"+ log_id +"_" + class_type)
    print("*"*15)
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if load_dict.__contains__("class_list_"+ dataset_name +'_'+ method +"_"+ log_id +"_" + class_type) == False:
        return JsonResponse({'code':200, 'msg':'There is no data', 'count':0, 'data':list([]) })
    
    return_list = load_dict["class_list_"+ dataset_name +'_'+ method +"_"+ log_id +"_"+ class_type]
    
    count = len(return_list)
    paginator = Paginator(return_list, limit)
    return_list = paginator.get_page(page)

    results = {}
    results['code'] = 0
    results['msg'] = ''
    results['count'] = count
    results['data'] = list(return_list)
    return JsonResponse(results)

@csrf_exempt
def model_analysis_getTextListByDatasetNameAndMethodAndLabel(request):
    print('model_analysis_getTableResultsByDatasetNameAndMethod')
    dataset_name = request.GET.get('dataset_name')
    method = request.GET.get('method')
    log_id = request.GET.get("log_id")
    label = request.GET.get('label_name')
    class_type = 'known'
    page = request.GET.get('page')
    limit = request.GET.get("limit")
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'analysis_table_info_new.json')
    return_list = []
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    key = "text_list_"+ str(dataset_name) +'_'+ str(method) +"_"+ str(log_id) +"_"+ str(class_type)+"_"+str(label)
    print("*"*15)
    print(key)
    print("*"*15)
    if load_dict.__contains__(key) == False:
        return JsonResponse({'code':200, 'msg':'There is no data', 'count':0, 'data':list([]) })
    
    # return_list = load_dict["class_list_"+ dataset_name +'_'+ method +"_"+ class_type+"_"+label]
    return_list = load_dict[key]
    
    count = len(return_list)
    paginator = Paginator(return_list, limit)
    return_list = paginator.get_page(page)

    results = {}
    results['code'] = 0
    results['msg'] = ''
    results['count'] = count
    results['data'] = list(return_list)
    return JsonResponse(results)


@csrf_exempt
def model_analysis_getDataOfADBByKey(request):
    print("lee--------------------570")
    key = request.GET.get('key')           
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'ADB_analysis.json')
    data_ADB = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_ADB = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_ADB
    return JsonResponse(results)


@csrf_exempt
def model_analysis_getDataOfMSPByKey(request):
    print("MSP--------------------589")
    key = request.GET.get('key')           
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'MSP_analysis_new.json')
    data_chart = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_chart = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_chart
    return JsonResponse(results)


@csrf_exempt
def model_analysis_getDataOfDeepUnkByKey(request):
    print("Deepunk--------------------570")
    key = request.GET.get('key')           
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'DeepUnk_analysis_new.json')
    data_chart = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_chart = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_chart
    return JsonResponse(results)

@csrf_exempt
def model_analysis_getDataOfDOCByKey(request):
    print("DOC--------------------626")
    key = request.GET.get('key')           
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'DOC_analysis_new.json')
    data_chart = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_chart = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_chart
    return JsonResponse(results)

@csrf_exempt
def model_analysis_getDataOfOpenMaxByKey(request):
    print("lee--------------------570")
    key = request.GET.get('key')           
    json_path = os.path.join(sys.path[0], 'static/jsons/open_intent_detection/', 'OpenMax_new.json')
    data_chart = {}
    with open(json_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if not load_dict.__contains__(key):
        return JsonResponse({ "code":201, "msg": "There is no data" })
    data_chart = load_dict[key]
    
    results = {}
    results['code'] = 200
    results['msg'] = ''
    results['data'] = data_chart
    return JsonResponse(results)





