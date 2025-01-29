import './PdfUploadButton.css';

export default function PdfUploadButton({ addFileName }) {
    function sendPdfToBackend(event) {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const file = formData.get('fileName');
        formData.append('file', file);

        if (!file.name) {
            alert('Please select a file before submitting.');
            return;
        }

        fetch('http://localhost:8000/api/upload', {
            method: 'POST',
            body: formData,
            credentials: 'include',
            enctype: 'multipart/form-data',
        })
        .then(response => {
            if (!response.ok) {
                alert('Failed to upload file');
                console.log(new Error('Failed to upload file'))
                return;
            }
            addFileName(file.name);
        });
    }

    return (
        <div>
            <form onSubmit={sendPdfToBackend}>
                <input type="file" name="fileName" accept=".pdf" />
                <input type="submit" />
            </form>
        </div>
    );
}
