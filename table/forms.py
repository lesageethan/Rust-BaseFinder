from django import forms

class SubmissionForm(forms.Form):
    name = forms.CharField(max_length=32)
    link = forms.CharField(max_length=128)
    creator = forms.CharField(max_length=128)
    group_size = forms.IntegerField()

    build_cost_stone = forms.IntegerField()
    build_cost_frags = forms.IntegerField()
    build_cost_hqm = forms.IntegerField()

    upkeep_cost_stone = forms.IntegerField()
    upkeep_cost_frags = forms.IntegerField()
    upkeep_cost_hqm = forms.IntegerField()

    raid_cost = forms.IntegerField()

    feature_1 = forms.CharField(max_length=32)
    feature_2 = forms.CharField(max_length=32)
    feature_3 = forms.CharField(max_length=32)

    fortify_link = forms.CharField(max_length=32, required=False)

class SearchForm(forms.Form):
    request_group_size = forms.IntegerField()
    
    budget_stone = forms.IntegerField()
    budget_frags = forms.IntegerField()
    budget_hqm = forms.IntegerField()

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=16)
    password = forms.CharField(max_length=16)
    email = forms.CharField(max_length=32)

class LogInForm(forms.Form):
    username = forms.CharField(max_length=16)
    password = forms.CharField(max_length=16)

class RatingForm(forms.Form):
    stars = forms.IntegerField()
    content = forms.CharField(max_length=512)