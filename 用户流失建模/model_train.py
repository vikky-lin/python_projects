# from sklearn.ensemble import GradientBoostingClassifier
from sklearn import *
from sklearn import ensemble
from scipy import interp  
import pandas as pd 
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import KFold
from sklearn.externals import joblib
from sklearn import metrics
import numpy as np
import   matplotlib.pyplot as plt

df = pd.read_csv('./data/training_data.csv')
train_x = df.iloc[:,:-1]
train_y = df['class']
params = {

}
clf = ensemble.GradientBoostingClassifier()
kf = KFold(train_x.shape[0],5)

mean_tpr = 0.0  
mean_fpr = np.linspace(0, 1, 100)  
all_tpr = []  
for index,(train,test) in enumerate(kf,1):
    train_set_x = train_x.iloc[train]
    train_set_y = train_y.iloc[train]
    test_set_x = train_x.iloc[test]
    test_set_y = train_y.iloc[test]
    clf.fit(train_set_x,train_set_y)    
    test_predict = clf.predict(test_set_x)
    # score = clf.score(test_set_x,test_set_y)
    #混淆矩阵
    confusion_matrix = metrics.confusion_matrix(test_set_y,test_predict)
    #F1 score
    f1_score = metrics.f1_score(test_set_y,test_predict)
    print('*********第%s轮**************'%index)
    print('混淆矩阵:\n%s'%confusion_matrix)
    print('F1 score:\n%s'%f1_score)

    #绘制roc曲线
    fpr, tpr, thresholds = metrics.roc_curve(test_set_y,test_predict)  
    mean_tpr += interp(mean_fpr, fpr, tpr)     
    mean_tpr[0] = 0.0                          
    roc_auc = metrics.auc(fpr, tpr) 
    plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (index, roc_auc))  
plt.show()

# train_x,test_x,train_y,test_y = train_test_split(train_x,train_y,train_size=0.7)
# clf = ensemble.GradientBoostingClassifier()
# clf.fit(train_x,train_y)
# joblib.dump(clf,'./model/gdbt_model.m')
# predict_y = clf.predict(test_x)