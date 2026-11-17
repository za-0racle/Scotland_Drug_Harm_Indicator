export async function openSupporting(page,selector){
 const details=page.locator(selector).first().locator('xpath=ancestor::details[contains(@class,"supporting-analysis")][1]');
 if(await details.count()&&!await details.evaluate(node=>node.open))await details.locator(':scope > summary').click();
}
