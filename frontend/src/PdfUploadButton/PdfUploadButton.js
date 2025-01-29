import './PdfUploadButton.css';

export default function PdfUploadButton({ addFileName }) {
    return (
        <div>
            <form>
                <input type="file" name="filename" accept=".pdf" />
                <input type="submit" />
            </form>
        </div>
    );
}
