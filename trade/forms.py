from django import forms
from trade.models.trade import Trade

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