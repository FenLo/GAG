const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('habertest')
        .setDescription('Haber sistemini manuel olarak test eder.')
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        await interaction.reply({
            content: '📰 Haber testi özelliği henüz geliştirilme aşamasındadır.',
            ephemeral: true
        });
    }
};
