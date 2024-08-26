
"""
# helper functions for jupyter notebook
# by Lev Selector, 2019
"""

import sys, os
import pandas as pd
import numpy as np
import time, glob, re, pickle, itertools, math
import datetime as dt

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

import sklearn
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# conda install -c conda-forge xgboost 
from xgboost.sklearn import XGBClassifier

from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split

from sklearn import metrics
from scipy.stats import ks_2samp  # two identify essential features

from util_jupyter import *

# --------------------------------------------------------------
def sigmoid(t):
    """
    # sigmoid function - can work on arrays and on individual numbers
    """
    s = 1.0 / (1.0 + np.exp(-t))
    return s

# --------------------------------------------------------------
def show_histogram(y):
    """ shows histogram of an array or a list (of numbers or strings, etc.)"""
    plt.rcParams["figure.figsize"] = (4, 4) # (width, height)
    plt.rcParams['font.size'] = 12
    fig, ax = plt.subplots()
    ax.hist(y, bins=100)
    ax.set_title('Histogram')
    fig.tight_layout()
    plt.show()

# --------------------------------------------------------------
def show_roc_curve(target=None, predict_proba=None):
    """
    # ROC curve = (Receiver Operating Characteristic curve)
    # was first developed during World War II for detecting enemy objects in battlefields.
    # plotting True Positive Rate (TPR) vs False Positive Rate (FPR) at various thresholds.
    # TPR a.k.a. sensitivity, recall, or probability of detection.
    # FPR a.k.a fall-out or probability of false alarm = (1-specificity).
    # So ROC curve is the sensitivity as a function of fall-out.
    """
    fpr, tpr, thresholds = metrics.roc_curve(target, predict_proba)
    plt.rcParams["figure.figsize"] = (4, 4) # (width, height)
    plt.plot(fpr, tpr, linewidth=3.0, color='red')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.title('ROC Curve')
    plt.xlabel('False Positive Rate (1 - Specificity)')
    plt.ylabel('True Positive Rate (Sensitivity)')
    plt.grid(True)
    plt.show()

# --------------------------------------------------------------
def plot_confusion_matrix(cm, mytitle=None, classes=None, saveas=None):
    """
    # print Confusion matrix with blue gradient colours
    # cm = metrics.confusion_matrix(y_expected, y_predicted)
    # plot_confusion_matrix(cm, mytitle="Some Title", saveas="SomeImage.png")
    """
    from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

    if mytitle == None:
        mytitle = "Confusion Matrix"
    if classes == None:
        classes = ['0','1']
    cmap=plt.cm.Blues
    if type(cm) == list:
        cm = np.array(cm)
    cm_orig = cm.copy()
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.rcParams["figure.figsize"] = (4, 4) # (width, height)
    fig,ax = plt.subplots()
    # _ = ax.scatter(x1,x2, marker='.')
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.set_title(mytitle)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.5)
    fig.colorbar(im, cax=cax, orientation='vertical')

    ax.set_xticks([0,1])
    ax.set_xticklabels(classes)
    ax.set_yticks([0,1])
    ax.set_yticklabels(classes)

    fmt = '.1%'
    thresh = 0.5*(cm.max()+cm.min())
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        mytext = str(cm_orig[i, j]) + ' / ' + format(cm[i, j], fmt)
        ax.text(j, i, mytext,
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black"
                 # , backgroundcolor="navy" if cm[i, j] > thresh else "aliceblue"
                 # , weight="bold"
                )

    plt.tight_layout()
    ax.set_ylabel('Actual (True, Exptected)')
    ax.set_xlabel('Predicted (Model)')
    plt.show();
    
    if saveas != None:
        plt.savefig(saveas, dpi=100)

# --------------------------------------------------------------
def run_cv(df, model, label, columns, repeat = 1):
    """
    #  runs model
    #  gets data from external DataFrame df:
    #      X => df[columns]
    #      Y => df['Class']
    #  goess through n_cv folds
    #  repeats "repeat" times
    #  (12 calculations, if n_cv=4, and repeat=3)
    #  returns dictionary "res" 
    #      keys   [precision, recall, f1core]
    #      values as tuples (mean, std_deviation)
    """   
    print("running ", label)
    t1=time.time()
    precisions = []
    recalls = []
    f1scores = []
    seconds    = []
    n_cv = len(df.cv_fold.unique())

    for cycle in range(repeat):
        # ----------------------------
        for n in range(n_cv):
            tt=time.time()
            print("(rep=%d, fold=%d), " % (cycle,n), end='')
            X_train = df[df.cv_fold != n][columns]
            Y_train = df[df.cv_fold != n]['Class']
            X_test  = df[df.cv_fold == n][columns]
            Y_test  = df[df.cv_fold == n]['Class']
            model.fit(X_train, Y_train)

            Y_predict = model.predict(X_test)
            rs  = metrics.recall_score   (Y_test, Y_predict)
            ps  = metrics.precision_score(Y_test, Y_predict)
            fs  = metrics.f1_score       (Y_test, Y_predict)
            dtt = time.time() - tt
            print("precision=%.3f, recall=%.3f, f1score=%.3f, %.2fsec" % (ps,rs,fs,dtt), end='')
            print('confusion matrix', sklearn)
            recalls.append    (rs)
            precisions.append (ps)
            f1scores.append   (fs)
            seconds.append    (dtt)
            print()
        # ----------------------------

    res = {}
    res['precision'] = (np.mean(precisions), np.std(precisions))
    res['recall']    = (np.mean(recalls)   , np.std(recalls))
    res['f1score']   = (np.mean(f1scores)  , np.std(f1scores))
    res['seconds']   = (np.mean(seconds)   , np.std(seconds))

    print("\nfinished %d calculations" % (repeat*n_cv))
    print ("Precision : %.6f +- %.6f" % res['precision'])
    print ("Recall    : %.6f +- %.6f" % res['recall'   ])
    print ("F1 score  : %.6f +- %.6f" % res['f1score'  ])
    print ("Seconds   : %.6f +- %.6f" % res['seconds'  ])

    expected  = Y_test 
    predicted = Y_predict
    confusion = metrics.confusion_matrix(expected, predicted)
    print(confusion)
    plot_confusion_matrix(confusion)

    print("Elapsed %.2f sec" % (time.time()-t1) )
    print('-'*65,"\n")
    return res

# --------------------------------------------------------------
def run_cv_wrapper(df, model, results, cols, repeat=1):
    model_name = model.__class__.__name__
    print("model_name =",model_name)
    results[model_name] = run_cv(df, model, model_name, cols, repeat = repeat)

# --------------------------------------------------------------
def run_stuff(df, models=None, repeat=1):
    """
    # accepts pandas DataFrame with one column "Class"
    # and several numeric feature columns
    # runs several models identified 
    # in model_names by short strings: 
    #     'lg' for Logistic Regression
    #     'rf' for Random Forest
    #     'xgb' for XGBoost
    # accumulates results over 4 folds
    # displays summary results
    # returns list of tuples (model_name, model_object)
    """
    if models == None:
        models=['rf']

    # Create Cross-Validation Folds
    # We randomly split all data rows in 4 groups (folds) numbered as 0,1,2,3 
    # For modeling we will randomly select one of the folds as test data, 
    # and combination of other three folds as training data. 
    # Thus we can repeat modeling 4 times (if there are 4 folds). 
    n_cv = 4           # number of cross-validation folds
    df_len = len(df)   # length of data
    df['cv_fold'] = np.random.randint(0,4, df_len)  

    results = {}
    models_objects = []
    cols = sorted(set(list(df.columns)) - set(['Class']))
    df_orig = df.copy()

    if 'lg' in models:
        df = df_orig.copy()
        model = LogisticRegression(class_weight="balanced", solver='lbfgs', C=10)
        run_cv_wrapper(df, model, results, cols, repeat=repeat)
        models_objects += [('lg',model)]

    if 'rf' in models:
        df = df_orig.copy()
        model = RandomForestClassifier(n_estimators=200)
        run_cv_wrapper(df, model, results, cols, repeat=repeat)
        models_objects += [('rf',model)]

    if 'xgb' in models:
        df = df_orig.copy()
        os.environ['KMP_DUPLICATE_LIB_OK']='True'
        params = {'eta':0.03,'objective':'binary:logistic','eval_metric':'auc','max_depth':15}
        model = XGBClassifier(**params) 
        run_cv_wrapper(df, model, results, cols, repeat=repeat)
        models_objects += [('xgb',model)]

    df = df_orig.copy()
    del df_orig
    print("DONE")

    results_orig = results.copy()
    # round the results to 3 decimals
    for k1 in results.keys():
        for k2 in results[k1].keys():
            (v1,v2) = results[k1][k2]
            results[k1][k2] = (round(v1,3),round(v2,3))
    df_result = pd.DataFrame.from_dict(results)
    # print results as tuples (value, std), where std = Standard Deviation
    # for example (0.5, 0.1) means: 0.5 +/- 0.1
    display(df_result.transpose())

    return models_objects 

# --------------------------------------------------------------
def top_corollaries(df):
    """
    # accepts the DataFrame with features and "Class" column (0,1)
    # returns a list of columns which change their values the most
    # when we change from rows with Class==0 to Class==1.
    # returns dataframe with columns ['col','p_val'] sorted
    # by p_val with most important columns on top.
    #
    # To compare two distributions we will use Kolmogorov-Smirnov test.
    #  - https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test
    # Note - this is just one of many tests, for example, read this discussion:
    #  - https://stats.stackexchange.com/questions/1001/is-spearmans-correlation-coefficient-usable-to-compare-distributions
    # 
    # function ks_2samp(array1, array2) 
    # compares distributions of values in two arrays
    # and returns p_value
    #    p_value > 0.4 - distributions are very similar (identical)
    #    p_value very small - distributions differ
    """
    ks = []
    cols = sorted(set(list(df.columns)) - set(['Class']))
    for col in cols:
        vals_0 = df[df.Class == 0][col].values  # values for column <col> for rows where Class==0
        vals_1 = df[df.Class == 1][col].values  # values for column <col> for rows where Class==1
        p_val = ks_2samp(vals_0, vals_1)[0] # higher value for similar distributions
        ks.append((col, p_val))
        print("%s => %.6f" % (col,p_val))
    # pick 10 most correlated variables.
    # create DataFrame [label, p_val]
    df_ks = pd.DataFrame(data = ks, columns = ['col', 'p_val'])
    # sort by p_val in decreasing order
    df_ks = df_ks.sort_values(by='p_val',ascending=False)
    return df_ks