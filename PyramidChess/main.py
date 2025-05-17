from pyramidchess_data_generate import data_generate,check_file_structure
from optparse import OptionParser


def main():
    parser = OptionParser()
    parser.add_option('-e', '--example',       default=False,              help='Set dataset dir to \'pyramidchess_dataset_example/\'',      action='store_true', dest='example')
    parser.add_option('-p', '--policy',        default='Average',          help='Data generating policy (Random,Average)',                   action='store', type='string', dest='policy')
    # parser.add_option('-s', '--select',        default=False,              help='Use selected options else all options',                     action='store_true',   dest='select')
    parser.add_option('-q', '--questionType',  default='0,1,2,3,4,5',      help='Select which question type to be generate',                 action='store', type='string', dest='questionType')
    parser.add_option('-l', '--plotLevel',     default='Easy,Medium,Hard', help='Select which plot level to be generate',                    action='store', type='string', dest='plotLevel')
    parser.add_option('-n', '--numGenerate',   default=18,                 help='Number of data to be generate',                             action='store', type='int', dest='numGenerate')
    parser.add_option('-i', '--startId',       default=0,                  help='Id of the first data to be generate',                       action='store', type='int',    dest='id')
    (options, args) = parser.parse_args()
    print('OPTIONS example',      options.example)
    print('OPTIONS policy',       options.policy)
    # print('OPTIONS select',       options.select)
    print('OPTIONS questionType', options.questionType)
    print('OPTIONS plotLevel',    options.plotLevel)
    print('OPTIONS numGenerate',  options.numGenerate)
    print('OPTIONS startid',      options.id)
    
    check_file_structure(example=options.example)
    
    print('\nDataset Generation Start')
    
    QUESTION_ID = [int(x) for x in options.questionType.split(',')]
    PLOT_LEVEL = options.plotLevel.split(',')
    num_type = len(QUESTION_ID)
    num_type_plot = len(PLOT_LEVEL)
    if options.policy == "Random":
        print(f"Now generating: Select {QUESTION_ID}{PLOT_LEVEL} Random {options.numGenerate} in total")
        data_generate(num_question=options.numGenerate,start_id=options.id,example=options.example,question_id_list=QUESTION_ID,plot_level_list=PLOT_LEVEL,param_list=[0.25])
    elif options.policy == "Average": 
        new_id = options.id
        num_each_question = (int)(options.numGenerate / num_type)
        num_more = (int)(options.numGenerate % num_type)
        question_num = [num_each_question for i in range(num_type)]
        for i in range(num_more):
            question_num[i] += 1
        for qid in range(num_type):
            print(f"Now generating: question_type{QUESTION_ID[qid]} {question_num[qid]} in total")
            num_each_plotlevel = (int)(question_num[qid] / num_type_plot)
            num_more_plotlevel = (int)(question_num[qid] % num_type_plot)
            plotlevel_num = [num_each_plotlevel for i in range(num_type_plot)]
            for i in range(num_more_plotlevel):
                plotlevel_num[i] += 1
            for plv in range(num_type_plot):
                new_id = data_generate(num_question=plotlevel_num[plv],plot_level_list=[PLOT_LEVEL[plv]],question_id_list=[QUESTION_ID[qid]],start_id=new_id,example=options.example,param_list=[0.25])  
    else: 
        raise ValueError(f"Unsupported policy:{options.policy}")
        
    print('\nDataset Generation End')
                        
    
if __name__ == "__main__":
    main()