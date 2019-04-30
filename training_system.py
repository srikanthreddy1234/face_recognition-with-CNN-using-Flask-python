from preprocess import preprocesses
import sys
from classifier import training

def sys_train():
    try:
        input_datadir = './static/people_photo/train_img'
        output_datadir = './pre_img'

        obj=preprocesses(input_datadir,output_datadir)
        nrof_images_total,nrof_successfully_aligned=obj.collect_data()

        print('Total number of images: %d' % nrof_images_total)
        print('Number of successfully aligned images: %d' % nrof_successfully_aligned)

        datadir = './pre_img'
        modeldir = './model/20170511-185253.pb'
        classifier_filename = './class/classifier.pkl'
        print ("Training Start")
        obj=training(datadir,modeldir,classifier_filename)
        get_file=obj.main_train()
        print('Saved classifier model to file "%s"' % get_file)
        sys.exit("All Done")
    except:
        print(sys.exc_info()[0])