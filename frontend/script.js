document.addEventListener('DOMContentLoaded', () => {
    const churnForm = document.getElementById('churnForm');
    const submitBtn = document.getElementById('submitBtn');
    const resultPlaceholder = document.querySelector('.result-placeholder');
    const resultContent = document.getElementById('resultContent');
    const statusBadge = document.getElementById('statusBadge');
    const resultTitle = document.getElementById('resultTitle');
    const resultDesc = document.getElementById('resultDesc');
    const meterFill = document.getElementById('meterFill');

    churnForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI state: Loading
        submitBtn.disabled = true;
        submitBtn.textContent = 'Analyzing...';
        
        // Construct payload (using basic fields for the demo)
        // In a real app, you'd collect all 18 fields
        const formData = {
            gender: document.getElementById('gender').value,
            Partner: "No",
            Dependents: "No",
            PhoneService: "Yes",
            MultipleLines: "No",
            InternetService: document.getElementById('InternetService').value,
            OnlineSecurity: "No",
            OnlineBackup: "No",
            DeviceProtection: "No",
            TechSupport: "No",
            StreamingTV: "No",
            StreamingMovies: "No",
            Contract: document.getElementById('Contract').value,
            PaperlessBilling: "Yes",
            PaymentMethod: document.getElementById('PaymentMethod').value,
            tenure: parseInt(document.getElementById('tenure').value),
            MonthlyCharges: parseFloat(document.getElementById('MonthlyCharges').value),
            TotalCharges: parseFloat(document.getElementById('MonthlyCharges').value) * parseInt(document.getElementById('tenure').value)
        };

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.prediction) {
                showResult(data.prediction);
            } else {
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('Could not connect to the API. Make sure the server is running.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Analyze Risk';
        }
    });

    function showResult(prediction) {
        resultPlaceholder.classList.add('hidden');
        resultContent.classList.remove('hidden');

        // Reset classes
        statusBadge.className = 'status-badge';
        meterFill.className = 'meter-fill';

        if (prediction === "Likely to churn") {
            statusBadge.textContent = 'High Risk';
            statusBadge.classList.add('status-high');
            resultTitle.textContent = 'Customer at risk of leaving';
            resultDesc.textContent = 'Retention intervention is recommended. Suggest offering a contract extension or loyalty discount.';
            meterFill.classList.add('fill-high');
        } else {
            statusBadge.textContent = 'Low Risk';
            statusBadge.classList.add('status-low');
            resultTitle.textContent = 'High retention probability';
            resultDesc.textContent = 'This customer shows strong loyalty patterns. Maintain standard service protocols.';
            meterFill.classList.add('fill-low');
        }
    }
});
