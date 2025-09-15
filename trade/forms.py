from django import forms
from trade.models.trade import Trade
from trade.models.transactions import Transaction

class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['trade_type', 'symbol', 'amount', 'leverage', 'stop_loss', 'take_profit']
        widgets = {
            'trade_type': forms.RadioSelect(choices=Trade.TRADE_TYPE_CHOICES),
            'symbol': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1000'}),
            'leverage': forms.Select(attrs={'class': 'form-control'}),
            'stop_loss': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '46000'}),
            'take_profit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '48000'}),
        }

        def clean_amount(self):
            amount = self.cleaned_data.get('amount')
            if amount is None or amount <= 0:
                raise forms.ValidationError('Please enter a valid amount greater than 0.')
            return amount
        


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'currency', 'wallet_address'] 
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1000'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'wallet_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter or paste your crypto wallet'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError('Please enter a valid amount greater than 0.')
        return amount



class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'currency',
        ]
        widgets = {

            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1000'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError('Please enter a valid amount greater than 0.')
        return amount
    
