Classifier_Setup = RandomForestClassifier(
    max_depth=4,
    min_samples_leaf=8,
    min_samples_split=10,
    max_features=0.2,
    class_weight='balanced',
    n_estimators=100
)



