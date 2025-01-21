import './PdfUploadButton.css';

function PdfUploadButton() {
    return (
        <div>
            <form>
                <input type="file" name="filenames" accept=".pdf" multiple />
                <input type="submit" />
            </form>
        </div>
    );
}

export default PdfUploadButton;
